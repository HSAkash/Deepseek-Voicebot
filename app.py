import os
from pyprojroot import here
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
from accord.utils import get_config, create_history
import streamlit as st
from accord.chatbot import Chatbot
from accord.stt import STT
from accord.entity import (
    Role,
    Message,
    ChunkEvent
)

# Initialize floating features for the interface
float_init()
# Load configuration
config = get_config(here("configs/config.yaml"))
os.makedirs(config.stt.audio_root, exist_ok=True)

# Initialize chatbot
chatbot = Chatbot()

# Initialize Speech-to-Text (STT)
stt = STT()

WELCOME_MESSAGE = Message(role=Role.ASSISTANT, content="Hello, I'm accord. How can I help you today?")


st.header("Deepseek voice assistant")





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


# Create a container for the microphone and audio recording
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()


if audio_bytes:
    with st.spinner("Transcribing..."):
        # Write the audio bytes to a temporary file
        webm_file_path = here(config.stt.audio_file)
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)
        audio_bytes = None
        try:
            # Convert the audio to text using the speech_to_text function
            transcript = stt.transcribe(webm_file_path)
        except Exception as e:
            transcript = None
        os.remove(webm_file_path)
        if transcript:
            with st.chat_message("user", avatar="👤"):
                st.markdown(transcript)

            with st.chat_message("assistant", avatar="🤖"):
                full_response = ""
                message_placeholder = st.empty()
                message_placeholder.status("Analysing", state="running")
                for event in chatbot.ask(transcript, st.session_state.messages):
                    if isinstance (event, ChunkEvent):
                        chunk = event.content
                        full_response += chunk
                        message_placeholder.markdown(full_response)