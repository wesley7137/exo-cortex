from TTS.api import TTS
import logging
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import logging
import sounddevice as sd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/combined_listen.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class VoiceInterface:
    def __init__(self):
        # Remove the sr.Recognizer() as we won't be using it anymore
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        # Load Whisper model and processor
        model_id = "openai/whisper-large-v3-turbo"
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True
        )
        self.model.to(self.device)
        self.processor = AutoProcessor.from_pretrained(model_id)

        # Set up pipeline for Whisper transcription
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            chunk_length_s=30,
            batch_size=16,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )

    def listen(self, duration=5, sample_rate=16000):
        try:
            print("Listening...")
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
            sd.wait()
            audio_data = audio_data.flatten()

            # Transcribe using Whisper model
            result = self.pipe(audio_data)
            text = result["text"]

            logger.info(f"Recognized speech: {text}")
            return text
        except Exception as e:
            logger.error(f"Error in listen: {e}")
            return None

    def speak(self, text):
        try:
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
            tts.tts_to_file(
                text=text,
                file_path="output.wav",
                speaker_wav="/path/to/target/speaker.wav",
                language="en"
            )
            logger.info(f"Spoken text: {text}")
        except Exception as e:
            logger.error(f"Error in speak: {e}")





