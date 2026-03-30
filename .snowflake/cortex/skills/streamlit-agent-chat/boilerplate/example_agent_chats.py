"""
Example: Cortex Agent Chat in Streamlit Tabs

This example demonstrates how to integrate multiple Cortex Agent chats
into different tabs of a Streamlit application.

- Tab 1: Uses connections.toml file
- Tab 2: Uses direct credentials (environment variables or Streamlit secrets)
- Tab 3: Uses connections.toml file
"""

import os
import streamlit as st
from cortex_agent_chat import CortexAgentChat

st.set_page_config(
    page_title="Multi-Agent Dashboard",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Agent Dashboard")
st.markdown("Chat with different specialized agents in separate tabs")

# Create tabs
tab1, tab2 = st.tabs(["📊 Sales Agent (TOML)", "💊 Clinical Agent (Direct)"])

# Tab 1: Sales Intelligence Agent
with tab1:
    st.header("Sales Intelligence Agent")
    st.markdown("Ask questions about sales metrics and conversations")
    
    # Create chat instance with unique session key for this tab
    sales_chat = CortexAgentChat.from_toml_connection(
        connection_name="LSDEMO",
        database="snowflake_intelligence",
        schema="agents",
        agent="gsk_clinical_agent",
        session_key="sales_agent_messages",
        title=None,  # We already have a header
        chat_input_placeholder="Ask about sales metrics..."
    )
    
    # Add a clear button
    if st.button("🗑️ Clear Chat", key="clear_sales"):
        sales_chat.clear_history()
        st.rerun()
    
    sales_chat.render()

# Tab 2: Clinical Agent (using direct credentials - no connection file)
with tab2:
    st.header("Clinical Data Agent")
    st.markdown("Get insights from clinical trial data")
    st.info("💡 This tab demonstrates using direct credentials instead of connections.toml")
    
    # Get credentials from environment variables or Streamlit secrets
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        PAT = st.secrets.get("snowflake", {}).get("pat") or os.getenv("SNOWFLAKE_PAT")
        HOST = st.secrets.get("snowflake", {}).get("host") or os.getenv("SNOWFLAKE_HOST")
    except:
        # Fallback to environment variables only
        PAT = os.getenv("SNOWFLAKE_PAT")
        HOST = os.getenv("SNOWFLAKE_HOST")
    
    if PAT and HOST:
        clinical_chat = CortexAgentChat(
            pat=PAT,
            host=HOST,
            database="snowflake_intelligence",
            schema="agents",
            agent="GSK_CLINICAL_AGENT",
            session_key="clinical_agent_messages",
            title=None,
            chat_input_placeholder="Ask about clinical trials..."
        )
        
        if st.button("🗑️ Clear Chat", key="clear_clinical"):
            clinical_chat.clear_history()
            st.rerun()
        
        clinical_chat.render()
    else:
        st.error("""
        Missing credentials! Set environment variables:
        ```bash
        export SNOWFLAKE_PAT="your_token"
        export SNOWFLAKE_HOST="account.snowflakecomputing.com"
        ```
        Or add to `.streamlit/secrets.toml`:
        ```toml
        [snowflake]
        pat = "your_token"
        host = "account.snowflakecomputing.com"
        ```
        """)
        clinical_chat = None

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This dashboard demonstrates two different authentication methods:
    
    **Tab 1 - Sales Agent:**
    - Uses `from_toml_connection()`
    - Credentials from `~/.snowflake/connections.toml`
    - Best for local development with Snowflake CLI
    
    **Tab 2 - Clinical Agent:**
    - Uses direct `CortexAgentChat()` constructor
    - Credentials from environment variables or Streamlit secrets
    - Best for deployments (Cloud, Docker, etc.)
    
    Each agent maintains its own conversation history.
    """)
    
    # Show message counts
    st.divider()
    st.subheader("Conversation Stats")
    st.metric("Sales Messages", sales_chat.get_message_count())
    if clinical_chat:
        st.metric("Clinical Messages", clinical_chat.get_message_count())
    else:
        st.caption("Clinical agent not configured")

