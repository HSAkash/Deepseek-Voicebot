import os
from pyprojroot import here
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
from accord.utils import get_config, create_history
import streamlit as st
from accord.chatbot import Chatbot
from accord.entity import (
    Role,
    Message,
    ChunkEvent
)


# Load configuration
config = get_config(here("configs/config.yaml"))
os.makedirs(config.stt.audio_root, exist_ok=True)

# Initialize chatbot
chatbot = Chatbot()

WELCOME_MESSAGE = Message(role=Role.ASSISTANT, content="Hello, I'm accord. How can I help you today?")

# Streamlit configuration
st.set_page_config(
    page_title="Accord",
    page_icon=":shark:",
    layout="centered",
    initial_sidebar_state="auto",
)

st.header("Accord RAG")
st.subheader("Get info from Documents")




# Display chat history at the top
if "messages" not in st.session_state:
    st.session_state.messages = create_history(WELCOME_MESSAGE)

for message in st.session_state.messages:
    avatar = "🤖" if message.role == Role.ASSISTANT else "👤"
    with st.chat_message(message.role.value, avatar=avatar):
        st.markdown(message.content)






if prompt := st.chat_input("Type your message..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        full_response = ""
        message_placeholder = st.empty()
        message_placeholder.status("Analysing", state="running")
        for event in chatbot.ask(prompt, st.session_state.messages):
            if isinstance (event, ChunkEvent):
                chunk = event.content
                full_response += chunk
                message_placeholder.markdown(full_response)





