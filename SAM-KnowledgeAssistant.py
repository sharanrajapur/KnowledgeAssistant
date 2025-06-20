import streamlit as st
import requests
import uuid
import json

# --- Configuration ---
API_URL = "https://elastic.snaplogic.com/api/1/rest/slsched/feed/SIE_Health_Dev/SHS_IT_DCE_PM/Agents/AgentDriver_KnowledgeAssistantTask"
API_TOKEN = "hgZhueHVdL0K5b4CXbTQDQtt2x47myOg" # Replace with your actual token if it changes

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="SAM AI Knowledge Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 SAM AI Knowledge Assistant")
st.caption("Your intelligent partner for accessing information.")

# --- Agent Description ---
st.markdown("""
Welcome! I am a specialized AI agent designed to support the Sales and Marketing department at Siemens Healthineers. I can answer questions about customers, products, and sales data using a set of powerful internal tools.
""")
st.markdown("---")


# --- Session State Initialization ---
# This ensures that the session_id and messages persist across reruns
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- Helper Function to Call API ---
def get_assistant_response(session_id, messages):
    """
    Sends the conversation history to the backend API and gets a response.
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    # The API expects a list containing a single JSON object
    payload = [{
        "session_id": session_id,
        "messages": messages
    }]

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=120)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        # The actual response from the API is a string inside a JSON object.
        response_data = response.json()
        if response_data and 'response' in response_data:
            return response_data['response']
        else:
            return "Error: Received an unexpected response format from the server."

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the API. Error: {e}")
        return None

# --- Display Chat History ---
# This loop iterates through the messages stored in the session state
for message in st.session_state.messages:
    with st.chat_message(message["sl_role"].lower()):
        st.markdown(message["content"])

# --- Example Prompts ---
st.markdown("#### Try an example:")
prompt1_text = "Which customers are using the CIARTIC Move product?"
prompt2_text = "Show me all 'Booked' opportunities for the product 'ARTIS icono biplane' and their funnel value."
prompt3_text = "What products does Universitätsklinikum Ulm A.d.ö.R. use?"

submitted_prompt = None

cols = st.columns([1, 1.3, 1]) # Adjust column widths for better text fit
with cols[0]:
    if st.button(prompt1_text, use_container_width=True):
        submitted_prompt = prompt1_text
with cols[1]:
    if st.button(prompt2_text, use_container_width=True):
        submitted_prompt = prompt2_text
with cols[2]:
    if st.button(prompt3_text, use_container_width=True):
         submitted_prompt = prompt3_text

# --- User Input Handling ---
# Get prompt from chat input if no button was pressed
chat_prompt = st.chat_input("Or ask your own question here...")
if chat_prompt:
    submitted_prompt = chat_prompt

if submitted_prompt:
    # 1. Add user message to the session state and display it
    user_message = {"sl_role": "USER", "content": submitted_prompt}
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(submitted_prompt)

    # 2. Get assistant's response
    with st.spinner("Thinking..."):
        assistant_response_content = get_assistant_response(
            st.session_state.session_id,
            st.session_state.messages
        )

    # 3. Add assistant message to the session state and display it
    if assistant_response_content:
        assistant_message = {"sl_role": "ASSISTANT", "content": assistant_response_content}
        st.session_state.messages.append(assistant_message)
        with st.chat_message("assistant"):
            st.markdown(assistant_response_content)
    else:
        st.error("Could not retrieve a response. Please try again.")

# --- Sidebar for session management ---
with st.sidebar:
    st.header("Session Control")
    st.write(f"**Session ID:**")
    st.code(st.session_state.session_id)
    st.markdown("---")
    if st.button("Start New Conversation"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.info("Each conversation has a unique session ID. Click the button above to clear the history and start fresh.")
