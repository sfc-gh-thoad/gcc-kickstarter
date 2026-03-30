"""
Reusable Cortex Agent Chat Component for Streamlit

This module provides a reusable chat interface for Snowflake Cortex Agents
that can be easily integrated into any Streamlit application.

Example usage:
    from cortex_agent_chat import CortexAgentChat
    
    # Use connections.toml for credentials, specify agent in code
    chat = CortexAgentChat.from_toml_connection(
        connection_name="LSDEMO",
        database="snowflake_intelligence",
        schema="agents",
        agent="MY_AGENT"
    )
    chat.render()
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests
import sseclient
import streamlit as st

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from models import (
    ChartEventData,
    DataAgentRunRequest,
    ErrorEventData,
    Message,
    MessageContentItem,
    StatusEventData,
    TableEventData,
    TextContentItem,
    TextDeltaEventData,
    ThinkingDeltaEventData,
    ThinkingEventData,
    ToolResultEventData,
    ToolUseEventData,
)


def strip_annotations_from_message(message: Message) -> Message:
    """Strip annotations from a Message to avoid server-side parsing errors.

    When Cortex Search or Web Search returns citations, the annotations on
    TextContentItem cannot be re-parsed by the server if sent back as
    conversation history (causes oneOf(Annotation) unmarshal error).

    Citations are still displayed in real-time during SSE streaming — they
    are only stripped from the stored history to prevent follow-up crashes.
    """
    cleaned_content = []
    for content_item in message.content:
        if content_item.actual_instance is not None:
            actual = content_item.actual_instance
            if isinstance(actual, TextContentItem):
                cleaned_text = TextContentItem(
                    text=actual.text,
                    annotations=None,
                    is_elicitation=actual.is_elicitation,
                    type=actual.type,
                )
                cleaned_content.append(MessageContentItem(cleaned_text))
            else:
                cleaned_content.append(content_item)
        else:
            cleaned_content.append(content_item)

    return Message(
        role=message.role,
        content=cleaned_content,
        schema_version=message.schema_version,
    )


class CortexAgentChat:
    """
    A reusable chat component for Snowflake Cortex Agents.
    
    This class encapsulates all the functionality needed to interact with
    a Cortex Agent via REST API and render the chat interface in Streamlit.
    
    Attributes:
        pat: Personal Access Token for authentication
        host: Snowflake account host
        database: Database containing the agent
        schema: Schema containing the agent
        agent: Agent name
        model: LLM model to use (default: claude-4-sonnet)
        session_key: Key for storing messages in st.session_state
    """
    
    def __init__(
        self,
        pat: str,
        host: str,
        database: str,
        schema: str,
        agent: str,
        model: str = "claude-4-sonnet",
        session_key: Optional[str] = None,
        title: Optional[str] = None,
        chat_input_placeholder: str = "What is your question?",
        verify_ssl: bool = False,
    ):
        """
        Initialize the Cortex Agent Chat component.
        
        Args:
            pat: Personal Access Token for authentication
            host: Snowflake account host (e.g., account.snowflakecomputing.com)
            database: Database containing the agent
            schema: Schema containing the agent
            agent: Agent name
            model: LLM model to use (default: claude-4-sonnet)
            session_key: Unique key for this chat instance in session state
            title: Title to display above the chat (optional)
            chat_input_placeholder: Placeholder text for chat input
            verify_ssl: Whether to verify SSL certificates
        """
        self.pat = pat
        self.host = host
        self.database = database
        self.schema = schema
        self.agent = agent
        self.model = model
        self.session_key = session_key or f"messages_{agent}"
        self.title = title or f"Chat with {agent}"
        self.chat_input_placeholder = chat_input_placeholder
        self.verify_ssl = verify_ssl
        
        # Initialize session state for this chat instance
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = []
    
    @classmethod
    def from_toml_connection(
        cls,
        connection_name: str,
        database: str,
        schema: str,
        agent: str,
        toml_path: str = "~/.snowflake/connections.toml",
        **kwargs
    ) -> "CortexAgentChat":
        """
        Create a CortexAgentChat instance directly from a connections.toml file.
        
        Args:
            connection_name: Name of the connection in connections.toml
            database: Database containing the agent
            schema: Schema containing the agent
            agent: Agent name
            toml_path: Path to connections.toml (default: ~/.snowflake/connections.toml)
            **kwargs: Additional arguments passed to __init__
        
        Returns:
            Configured CortexAgentChat instance
        """
        toml_path = Path(toml_path).expanduser()
        
        with open(toml_path, "rb") as f:
            connections = tomllib.load(f)
        
        conn_config = connections.get(connection_name, {})
        if not conn_config:
            raise ValueError(f"Connection '{connection_name}' not found in {toml_path}")
        
        pat = conn_config.get('password')
        account = conn_config.get('account', '')
        host = f"{account.lower()}.snowflakecomputing.com" if account else None
        
        return cls(
            pat=pat,
            host=host,
            database=database,
            schema=schema,
            agent=agent,
            **kwargs
        )
    
    def _agent_run(self) -> requests.Response:
        """
        Call the Cortex Agent REST API and return a streaming response.
        
        Returns:
            Streaming HTTP response
        
        Raises:
            Exception: If the API request fails
        """
        request_body = DataAgentRunRequest(
            model=self.model,
            messages=st.session_state[self.session_key],
        )
        resp = requests.post(
            url=f"https://{self.host}/api/v2/databases/{self.database}/schemas/{self.schema}/agents/{self.agent}:run",
            data=request_body.to_json(),
            headers={
                "Authorization": f'Bearer {self.pat}',
                "Content-Type": "application/json",
            },
            stream=True,
            verify=self.verify_ssl,
        )
        if resp.status_code < 400:
            return resp
        else:
            raise Exception(f"Failed request with status {resp.status_code}: {resp.text}")
    
    def _stream_events(self, response: requests.Response):
        """
        Process and render streaming events from the agent response.
        
        Args:
            response: Streaming HTTP response from the agent
        """
        content = st.container()
        content_map = defaultdict(content.empty)
        buffers = defaultdict(str)
        spinner = st.spinner("Waiting for response...")
        spinner.__enter__()
        
        events = sseclient.SSEClient(response).events()
        for event in events:
            match event.event:
                case "response.status":
                    spinner.__exit__(None, None, None)
                    data = StatusEventData.from_json(event.data)
                    spinner = st.spinner(data.message)
                    spinner.__enter__()
                case "response.text.delta":
                    data = TextDeltaEventData.from_json(event.data)
                    buffers[data.content_index] += data.text
                    content_map[data.content_index].write(buffers[data.content_index])
                case "response.thinking.delta":
                    data = ThinkingDeltaEventData.from_json(event.data)
                    buffers[data.content_index] += data.text
                    content_map[data.content_index].expander(
                        "Thinking", expanded=True
                    ).write(buffers[data.content_index])
                case "response.thinking":
                    data = ThinkingEventData.from_json(event.data)
                    content_map[data.content_index].expander("Thinking").write(data.text)
                case "response.tool_use":
                    data = ToolUseEventData.from_json(event.data)
                    content_map[data.content_index].expander("Tool use").json(data)
                case "response.tool_result":
                    data = ToolResultEventData.from_json(event.data)
                    content_map[data.content_index].expander("Tool result").json(data)
                case "response.chart":
                    data = ChartEventData.from_json(event.data)
                    spec = json.loads(data.chart_spec)
                    content_map[data.content_index].vega_lite_chart(
                        spec,
                        use_container_width=True,
                    )
                case "response.table":
                    data = TableEventData.from_json(event.data)
                    data_array = np.array(data.result_set.data)
                    column_names = [
                        col.name for col in data.result_set.result_set_meta_data.row_type
                    ]
                    content_map[data.content_index].dataframe(
                        pd.DataFrame(data_array, columns=column_names)
                    )
                case "error":
                    data = ErrorEventData.from_json(event.data)
                    st.error(f"Error: {data.message} (code: {data.code})")
                    st.session_state[self.session_key].pop()
                    return
                case "response":
                    data = Message.from_json(event.data)
                    cleaned_data = strip_annotations_from_message(data)
                    st.session_state[self.session_key].append(cleaned_data)
        spinner.__exit__(None, None, None)
    
    def _process_new_message(self, prompt: str) -> None:
        """
        Process a new user message and get agent response.
        
        Args:
            prompt: User's message text
        """
        message = Message(
            role="user",
            content=[MessageContentItem(TextContentItem(type="text", text=prompt))],
        )
        self._render_message(message)
        st.session_state[self.session_key].append(message)
        
        with st.chat_message("assistant"):
            with st.spinner("Sending request..."):
                response = self._agent_run()
            st.markdown(
                f"```request_id: {response.headers.get('X-Snowflake-Request-Id')}```"
            )
            self._stream_events(response)
    
    def _render_message(self, msg: Message):
        """
        Render a single message in the chat interface.
        
        Args:
            msg: Message object to render
        """
        with st.chat_message(msg.role):
            for content_item in msg.content:
                match content_item.actual_instance.type:
                    case "text":
                        st.markdown(content_item.actual_instance.text)
                    case "chart":
                        spec = json.loads(content_item.actual_instance.chart.chart_spec)
                        st.vega_lite_chart(spec, use_container_width=True)
                    case "table":
                        data_array = np.array(
                            content_item.actual_instance.table.result_set.data
                        )
                        column_names = [
                            col.name
                            for col in content_item.actual_instance.table.result_set.result_set_meta_data.row_type
                        ]
                        st.dataframe(pd.DataFrame(data_array, columns=column_names))
                    case _:
                        st.expander(content_item.actual_instance.type).json(
                            content_item.actual_instance.to_json()
                        )
    
    def render(self, container=None):
        """
        Render the complete chat interface.
        
        This method displays the chat title (if provided), conversation history,
        and chat input box. It handles user input and agent responses.
        
        Args:
            container: Optional Streamlit container to render in (for tabs/columns)
        """
        # Use provided container or default to main
        ctx = container if container is not None else st
        
        if self.title:
            ctx.title(self.title)
        
        # Render conversation history
        for message in st.session_state[self.session_key]:
            self._render_message(message)
        
        # Chat input
        if user_input := ctx.chat_input(self.chat_input_placeholder):
            self._process_new_message(prompt=user_input)
    
    def clear_history(self):
        """Clear the conversation history for this chat instance."""
        st.session_state[self.session_key] = []
    
    def get_message_count(self) -> int:
        """Get the number of messages in the conversation history."""
        return len(st.session_state[self.session_key])

