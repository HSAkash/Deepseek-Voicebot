import os
from pyprojroot import here
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init
from accord.utils import get_config, create_history
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

# Custom CSS for sticky input and scrollable chat history
st.markdown("""
<style>

/* Sticky input field at the bottom */
.sticky-input {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: white;
    padding: 10px;
    box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}
</style>
""", unsafe_allow_html=True)

st.header("Deepseek voice assistant")

# Chat history container
chat_container = st.container()
with chat_container:
    if "messages" not in st.session_state:
        st.session_state.messages = create_history(WELCOME_MESSAGE)

    for message in st.session_state.messages:
        avatar = "🤖" if message.role == Role.ASSISTANT else "👤"
        with st.chat_message(message.role.value, avatar=avatar):
            st.markdown(message.content)
    st.markdown('</div>', unsafe_allow_html=True)

# Sticky input field
input_container = st.container()
with input_container:
    st.markdown('<div class="sticky-input">', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])  # Adjust column ratios as needed

    with col1:
        prompt = st.chat_input("Type your message...", key="text_input")

    with col2:
        audio_bytes = audio_recorder(icon_size="2x", key="mic")  # Microphone icon

    st.markdown('</div>', unsafe_allow_html=True)

# Handle text input
if prompt:
    with chat_container:
        # Add user message to chat history
        st.session_state.messages.append(Message(role=Role.USER, content=prompt))
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant", avatar="🤖"):
            full_response = ""
            message_placeholder = st.empty()
            message_placeholder.status("Analysing", state="running")
            for event in chatbot.ask(prompt, st.session_state.messages):
                if isinstance(event, ChunkEvent):
                    chunk = event.content
                    full_response += chunk
                    message_placeholder.markdown(full_response)

            # Add assistant message to chat history
            st.session_state.messages.append(Message(role=Role.ASSISTANT, content=full_response))

# Handle voice input
if audio_bytes:
    with chat_container:
        with st.spinner("Transcribing..."):
            print("Transcribing...")
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
                # Add user message to chat history
                st.session_state.messages.append(Message(role=Role.USER, content=transcript))
                with st.chat_message("user", avatar="👤"):
                    st.markdown(transcript)

                # Generate assistant response
                with st.chat_message("assistant", avatar="🤖"):
                    full_response = ""
                    message_placeholder = st.empty()
                    message_placeholder.status("Analysing", state="running")
                    for event in chatbot.ask(transcript, st.session_state.messages):
                        if isinstance(event, ChunkEvent):
                            chunk = event.content
                            full_response += chunk
                            message_placeholder.markdown(full_response)

                    # Add assistant message to chat history
                    st.session_state.messages.append(Message(role=Role.ASSISTANT, content=full_response))