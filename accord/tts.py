import base64
from gtts import gTTS
import streamlit as st
from pyprojroot import here
from accord.utils import get_config


class TTS:
    """ Text to speech conversion"""

    def __init__(self):
        self.config = get_config(here("configs/config.yaml"))

    def speak(self, text: str, lang: str = "en", slow:bool=False, filePath=None) -> None:
        """Convert text to speech.

        Args:
            text (str): Text to be converted.
            lang (str, optional): Language of the text. Defaults to "en".
            slow (bool, optional): Slow down the speech. Defaults to False.
            filePath (str, optional): Path to save the audio file. Defaults to None.
        """
        filePath = filePath or self.config.tts.audio_file
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(filePath)

    def play_audio(self, filePath=None) -> None:
        """Play the audio file.
        
        Args:
            filePath (str, optional): Path to the audio file. Defaults to None.
        """
        filePath = filePath or self.config.tts.audio_file
        with open(filePath, "rb") as file:
            audio_bytes = file.read()
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        # st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
        md = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)