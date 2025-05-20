import streamlit as st
import requests

# App config
st.set_page_config(page_title="SAM Knowledge Assistant")

# SnapLogic API settings (UPDATED)
API_ENDPOINT = "https://elastic.snaplogic.com/api/1/rest/slsched/feed/SIE_Health_Dev/SHS_IT_DCE_PM/Agents/AgentDriver_KnowledgeAssistantTask"
API_TOKEN = "hgZhueHVdL0K5b4CXbTQDQtt2x47myOg"

# Function to call SnapLogic AI Agent with debugging
def send_message(prompt):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = [{"prompt": [prompt]}]  # Ensure this matches what SnapLogic expects

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()

        # Show raw response text in the UI
        st.markdown("### Raw Response Text")
        st.code(response.text)

        try:
            result = response.json()
            st.markdown("### Parsed JSON Response")
            st.json(result)

            if isinstance(result, dict):
                return result.get("response", str(result))
            elif isinstance(result, list):
                return str(result[0]) if result else "⚠️ Empty list response."
            else:
                return str(result)
        except ValueError:
            return response.text

    except requests.exceptions.RequestException as e:
        try:
            error_details = response.text
        except:
            error_details = str(e)
        return f"❌ API call failed.\n\nDetails:\n```\n{error_details}\n```"

# Session state to store chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# App title
st.title("SAM Knowledge Assistant powered by SnapLogic")

# Display chat history
for message in st.session_state.messages:
    role = "You" if message["role"] == "user" else "Agent"
    st.markdown(f"**{role}:** {message['content']}")

# Chat input
if prompt := st.chat_input("Ask a question about products, customers, or documentation..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Processing..."):
        response = send_message(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
