import torch
import torchaudio
from pyprojroot import here
from accord.utils import get_config
from transformers import WhisperProcessor, WhisperForConditionalGeneration

class STT:
    """ Speech to text conversion"""

    def __init__(self):
        self.config = get_config(here("configs/config.yaml"))

        # Check if a GPU is available, otherwise use CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load the Whisper model and processor
        self.processor = WhisperProcessor.from_pretrained(self.config.stt.model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(self.config.stt.model_name).to(self.device)
        
    
    def audio_preprocess(self, audio_file: str) -> torch.Tensor:
        """Preprocess the audio file.

        Args:
            audio_file (str): Path to the audio file.

        Returns:
            torch.Tensor: Preprocessed audio tensor.
        """
        # Load the audio file
        waveform, sample_rate = torchaudio.load(audio_file)

        # Convert to correct sampling rate (Whisper requires 16kHz)
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)

        return waveform
    
    def transcribe(self, audio_file: str) -> str:
        """Transcribe the audio file to text.

        Args:
            audio_file (str): Path to the audio file.

        Returns:
            str: Transcribed text.
        """
        # Preprocess the audio file
        waveform = self.audio_preprocess(audio_file)

        # Convert waveform to input features
        input_features = self.processor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt").input_features.to(self.device)

        # Generate transcription
        with torch.no_grad():
            predicted_ids = self.model.generate(input_features)

        # Decode the output
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

        return transcription
    

if __name__ == "__main__":
    stt = STT()
    transcribed_text = stt.transcribe(here("data/01.wav"))
    print(f"transcribed_text: {transcribed_text}")