---
name: streamlit-agent-chat
description: >
  Build Streamlit chat interfaces for Snowflake Cortex Agents. Use when: creating agent chat apps,
  integrating Cortex Agent REST API with SSE streaming, handling citations/annotations from Cortex Search
  and Web Search, multi-agent tab layouts, or debugging agent chat errors in Streamlit.
log_marker: SKILL_USED_STREAMLIT_AGENT_CHAT
---

# Streamlit Agent Chat

Build production-ready Streamlit chat interfaces that communicate with Snowflake Cortex Agents via REST API with Server-Sent Events (SSE) streaming.

## When to Use This Skill

- Building a Streamlit app with a Cortex Agent chat interface
- Integrating Cortex Agent REST API responses (text, tables, charts, thinking, tool use) into Streamlit
- Handling citation/annotation parsing from Cortex Search or Web Search tools
- Creating multi-agent dashboards with isolated chat histories
- Debugging SSE streaming or annotation-related crashes

## Boilerplate Code Location

The reusable component and OpenAPI-generated Pydantic models are bundled with this skill at:

```
~/.snowflake/cortex/skills/my_skills/streamlit-agent-chat/
├── SKILL.md                      # This skill file
└── boilerplate/                   # Ready-to-copy project files
    ├── cortex_agent_chat.py       # Reusable CortexAgentChat class
    ├── example_agent_chats.py     # Multi-agent tabs example
    ├── requirements.txt           # Dependencies
    ├── __init__.py
    └── models/                    # OpenAPI-generated Pydantic models (75+ files)
        ├── __init__.py
        ├── message.py             # Message(role, content, schema_version)
        ├── message_content_item.py # oneOf: Text|Thinking|ToolUse|ToolResult|Table|Chart|SuggestedQueries
        ├── text_content_item.py   # TextContentItem(text, annotations, is_elicitation, type)
        ├── annotation.py          # oneOf: CortexSearchCitation | WebSearchCitation
        ├── cortex_search_citation.py # CortexSearchCitation(index, search_result_id, doc_id, doc_title, text)
        ├── web_search_citation.py # WebSearchCitation(start_index, end_index, source_url, text)
        ├── data_agent_run_request.py # Request body for agent :run endpoint
        └── ...                    # Chart, Table, Thinking, Tool, Status, Error models
```

## Prerequisites

1. Copy the contents of `~/.snowflake/cortex/skills/my_skills/streamlit-agent-chat/boilerplate/` into your project directory:
   ```bash
   cp -r ~/.snowflake/cortex/skills/my_skills/streamlit-agent-chat/boilerplate/* /path/to/your/project/
   ```
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure `~/.snowflake/connections.toml` has a valid connection with a PAT token

## Quick Start

Minimal 3-line integration:

```python
import streamlit as st
from cortex_agent_chat import CortexAgentChat

chat = CortexAgentChat.from_toml_connection(
    connection_name="LSDEMO",
    database="snowflake_intelligence",
    schema="agents",
    agent="MY_AGENT"
)
chat.render()
```

Run with: `streamlit run app.py`

## API Reference

### CortexAgentChat Constructor

```python
CortexAgentChat(
    pat: str,                              # Personal Access Token
    host: str,                             # account.snowflakecomputing.com
    database: str,                         # Database containing the agent
    schema: str,                           # Schema containing the agent
    agent: str,                            # Agent name
    model: str = "claude-4-sonnet",        # LLM model
    session_key: Optional[str] = None,     # Unique key for session state isolation
    title: Optional[str] = None,           # Chat title (auto-generated if None)
    chat_input_placeholder: str = "What is your question?",
    verify_ssl: bool = False               # SSL verification
)
```

### Class Methods

**`from_toml_connection(connection_name, database, schema, agent, toml_path="~/.snowflake/connections.toml", **kwargs)`**
- Creates instance from `connections.toml` credentials
- The `password` field in TOML is used as the PAT token
- The `account` field is converted to `{account}.snowflakecomputing.com` host

### Instance Methods

| Method | Description |
|--------|-------------|
| `render(container=None)` | Render the full chat UI (title, history, input). Pass a container for tabs/columns. |
| `clear_history()` | Clear conversation history for this instance |
| `get_message_count() -> int` | Number of messages in conversation |

### REST API Call

The `_agent_run()` method sends a POST to:
```
https://{host}/api/v2/databases/{database}/schemas/{schema}/agents/{agent}:run
```

Request body uses `DataAgentRunRequest(model=..., messages=...)` serialized to JSON.
Response is an SSE stream processed by `_stream_events()`.

## SSE Event Types Reference

The `_stream_events()` method handles these events from the agent response:

| Event | Pydantic Model | Streamlit Rendering |
|-------|---------------|---------------------|
| `response.status` | `StatusEventData` | `st.spinner(data.message)` |
| `response.text.delta` | `TextDeltaEventData` | Accumulated text via `st.write()` |
| `response.thinking.delta` | `ThinkingDeltaEventData` | Accumulated text in `st.expander("Thinking")` |
| `response.thinking` | `ThinkingEventData` | Full text in `st.expander("Thinking")` |
| `response.tool_use` | `ToolUseEventData` | JSON in `st.expander("Tool use")` |
| `response.tool_result` | `ToolResultEventData` | JSON in `st.expander("Tool result")` |
| `response.chart` | `ChartEventData` | Vega-Lite chart via `st.vega_lite_chart()` |
| `response.table` | `TableEventData` | DataFrame via `st.dataframe()` |
| `error` | `ErrorEventData` | `st.error()`, pops last message from history |
| `response` | `Message` | Final message stored in session state |

**Streaming pattern:** Delta events use `content_index` to map content to the correct `st.empty()` placeholder, allowing multiple content blocks to stream simultaneously.

```python
content = st.container()
content_map = defaultdict(content.empty)
buffers = defaultdict(str)

# For text deltas:
buffers[data.content_index] += data.text
content_map[data.content_index].write(buffers[data.content_index])
```

## Annotation Stripping (Built-In)

The boilerplate `cortex_agent_chat.py` includes a built-in `strip_annotations_from_message()` function that automatically handles a known server-side issue with Cortex Search and Web Search citations.

**What it does:** When an agent uses Cortex Search or Web Search tools, the response includes `TextContentItem` objects with `annotations` (citations of type `CortexSearchCitation` or `WebSearchCitation`). These annotations cannot be round-tripped back to the server as conversation history — doing so causes a `oneOf(Annotation)` unmarshal error on follow-up messages. The function strips annotations before storing in `st.session_state`, while citations are still displayed to the user in real-time during SSE streaming.

**No action needed** — this is already applied in the `"response"` event handler in the boilerplate code. If you're extending `_stream_events()` or building a custom implementation, ensure you call `strip_annotations_from_message()` on the final `Message` before appending to session state:

```python
case "response":
    data = Message.from_json(event.data)
    cleaned_data = strip_annotations_from_message(data)
    st.session_state[self.session_key].append(cleaned_data)
```

## Integration Patterns

### Single Agent App

```python
import streamlit as st
from cortex_agent_chat import CortexAgentChat

st.set_page_config(page_title="Agent Chat", layout="wide")

chat = CortexAgentChat.from_toml_connection(
    connection_name="LSDEMO",
    database="snowflake_intelligence",
    schema="agents",
    agent="CLINICAL_TRIALS_AGENT"
)
chat.render()
```

### Multi-Agent Tabs

Each agent MUST have a unique `session_key` to maintain separate conversation histories:

```python
tab1, tab2 = st.tabs(["Sales Agent", "Clinical Agent"])

with tab1:
    sales = CortexAgentChat.from_toml_connection(
        connection_name="LSDEMO",
        database="snowflake_intelligence",
        schema="agents",
        agent="SALES_AGENT",
        session_key="sales"
    )
    sales.render()

with tab2:
    clinical = CortexAgentChat.from_toml_connection(
        connection_name="LSDEMO",
        database="snowflake_intelligence",
        schema="agents",
        agent="CLINICAL_AGENT",
        session_key="clinical"
    )
    clinical.render()
```

### Sidebar Chat with Dashboard

```python
st.header("Dashboard")
st.metric("Revenue", "$1.2M")
st.line_chart({"Sales": [100, 150, 200]})

with st.sidebar:
    st.header("AI Assistant")
    chat = CortexAgentChat.from_toml_connection(
        connection_name="LSDEMO",
        database="snowflake_intelligence",
        schema="agents",
        agent="MY_AGENT"
    )
    chat.render()
```

### Dynamic Agent Selection

```python
agent_name = st.selectbox("Select Agent", ["SALES", "CLINICAL", "ANALYTICS"])

chat = CortexAgentChat.from_toml_connection(
    connection_name="LSDEMO",
    database="snowflake_intelligence",
    schema="agents",
    agent=f"{agent_name}_AGENT",
    session_key=agent_name.lower()
)
chat.render()
```

### Chat with Clear Button

```python
chat = CortexAgentChat.from_toml_connection(
    connection_name="LSDEMO",
    database="snowflake_intelligence",
    schema="agents",
    agent="MY_AGENT"
)

if st.button("Clear Chat"):
    chat.clear_history()
    st.rerun()

chat.render()
```

## Pydantic Model Architecture

The models use a **oneOf discriminator pattern** via `actual_instance`:

```
Message
  ├── role: "user" | "assistant"
  ├── content: List[MessageContentItem]
  │     └── actual_instance: oneOf
  │           ├── TextContentItem (type="text")
  │           │     ├── text: str
  │           │     ├── annotations: Optional[List[Annotation]]
  │           │     │     └── actual_instance: oneOf
  │           │     │           ├── CortexSearchCitation
  │           │     │           └── WebSearchCitation
  │           │     └── is_elicitation: Optional[bool]
  │           ├── ThinkingContentItem (type="thinking")
  │           ├── ToolUseContentItem (type="tool_use")
  │           ├── ToolResultContentItem (type="tool_result")
  │           ├── TableContentItem (type="table")
  │           ├── ChartContentItem (type="chart")
  │           └── SuggestedQueriesContentItem (type="suggested_queries")
  └── schema_version: Optional[str]
```

When rendering stored messages, match on `content_item.actual_instance.type`:

```python
for content_item in msg.content:
    match content_item.actual_instance.type:
        case "text":
            st.markdown(content_item.actual_instance.text)
        case "chart":
            spec = json.loads(content_item.actual_instance.chart.chart_spec)
            st.vega_lite_chart(spec, use_container_width=True)
        case "table":
            data_array = np.array(content_item.actual_instance.table.result_set.data)
            columns = [col.name for col in content_item.actual_instance.table.result_set.result_set_meta_data.row_type]
            st.dataframe(pd.DataFrame(data_array, columns=columns))
        case _:
            st.expander(content_item.actual_instance.type).json(
                content_item.actual_instance.to_json()
            )
```

## Troubleshooting

### Follow-up messages crash with unmarshal error

**Symptom:** First response works, second message fails with `data failed to match schemas in oneOf(Annotation)`

**Cause:** Citations stored in session state cannot be re-parsed by the server. The boilerplate handles this automatically via `strip_annotations_from_message()`. If you're seeing this error, you may be using a custom implementation that doesn't strip annotations — see the "Annotation Stripping (Built-In)" section above.

### Multiple agents share conversation history

**Symptom:** Two agents show the same messages.

**Fix:** Use unique `session_key` for each agent instance.

### Authentication failed (401)

**Checks:**
- PAT token is valid and not expired
- Account name format: `account.snowflakecomputing.com`
- Token has access to the database/schema/agent
- Connection name in `connections.toml` matches exactly

### Agent not found (404)

**Checks:**
- Agent name, database, schema are correct (case-sensitive)
- You have permissions to access the agent
- Test access in Snowsight first

### SSL Certificate errors

**Fix:** Set `verify_ssl=False` for development:
```python
chat = CortexAgentChat(..., verify_ssl=False)
```

### Session state errors / stale data

**Fixes:**
- Clear browser cache
- Use `chat.clear_history()` to reset
- Restart the Streamlit server
- Check for `session_key` conflicts between instances

## Dependencies

```
pandas==2.0.3
numpy==1.25.2
requests==2.32.3
streamlit==1.40.0
sseclient-py==1.8.0
pydantic==2.7.3
urllib3>=2.1.0,<3.0.0
python_dateutil>=2.8.2
typing-extensions>=4.7.1
tomli>=1.1.0; python_version<'3.11'
```

## Related Skills

- `streamlit-development` — General Streamlit development patterns, testing, deployment
- `streamlit-snowflake-deploy-skill` — Deploying Streamlit apps to Snowflake
- `cortex-agent` — Creating and debugging Cortex Agents in Snowflake
- `snowflake-connections` — Setting up `connections.toml` authentication
