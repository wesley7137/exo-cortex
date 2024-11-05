import os
import logging
from openai import OpenAI
from config import stt_config
import tempfile
import torch
from faster_whisper import WhisperModel
from threading import Thread
from queue import Queue
import base64
import io

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable symbolic links on Windows for huggingface_hub
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Define torch configuration
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if torch.cuda.is_available() else "float32"

# Load Faster-Whisper model
stt_model = WhisperModel("distil-large-v3", device=device, compute_type=compute_type)

import io
from pydub import AudioSegment

import asyncio
from concurrent.futures import ThreadPoolExecutor

# Create a thread pool
thread_pool = ThreadPoolExecutor(max_workers=4)

async def stt_local_async(audio_data, language=None):
    async def transcribe_worker(audio_file_path):
        try:
            segments, info = await asyncio.get_event_loop().run_in_executor(
                thread_pool, stt_model.transcribe, audio_file_path, 1
            )
            return "".join(segment.text for segment in segments)
        except Exception as e:
            logger.error(f"Error in transcribe worker: {e}")
            return None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio_data)
            temp_audio_file_path = temp_audio_file.name

        transcription = await transcribe_worker(temp_audio_file_path)

        if transcription is not None:
            logger.info(f"Transcription completed: {transcription}")
        else:
            logger.error("Transcription failed")
            transcription = ""

        return transcription
    except Exception as e:
        logger.error(f"General error in STT: {e}")
        return ""
    finally:
        try:
            os.remove(temp_audio_file_path)
        except Exception as e:
            logger.error(f"Error removing temporary file: {e}")

async def stt_async(audio_data, language=None):
    logger.info(f"Speech-to-text request received. Provider: {stt_config.STT_PROVIDER}")
    
    try:
        if stt_config.STT_PROVIDER == 'openai':
            return await asyncio.to_thread(stt_openai, audio_data, language)
        elif stt_config.STT_PROVIDER == 'local':
            return await stt_local_async(audio_data, language)
        else:
            logger.error(f"Invalid speech-to-text provider: {stt_config.STT_PROVIDER}")
            raise ValueError(f"Invalid speech-to-text provider: {stt_config.STT_PROVIDER}")
    except Exception as e:
        if "Invalid file format" in str(e):
            logger.error(f"Error in speech-to-text: Invalid audio format. Please ensure the audio is in a supported format.")
        else:
            logger.error(f"Error in speech-to-text: {str(e)}")
        raise





def convert_to_wav(audio_data):
    try:
        # Load the audio data
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        # Export as WAV
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        return wav_buffer.getvalue()
    except Exception as e:
        logger.error(f"Error converting audio to WAV: {str(e)}")
        raise



def stt_openai(audio_data, language=None):
    logger.info("Transcribing audio using OpenAI API")
    client = OpenAI(api_key=stt_config.OPENAI_API_KEY)
    
    try:
        # Convert audio data to WAV format
        wav_data = convert_to_wav(audio_data)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(wav_data)
            temp_audio_file_path = temp_audio_file.name

        with open(temp_audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        return transcription.text
    except Exception as e:
        logger.error(f"Error in OpenAI speech-to-text: {str(e)}")
        raise
    finally:
        try:
            os.remove(temp_audio_file_path)
        except Exception as e:
            logger.error(f"Error removing temporary file: {e}")

def stt_local(audio_data, language=None):
    def transcribe_worker(audio_file_path, result_queue):
        try:
            segments, info = stt_model.transcribe(audio_file_path, beam_size=1)
            transcription = "".join(segment.text for segment in segments)
            result_queue.put(transcription)
        except Exception as e:
            logger.error(f"Error in transcribe worker: {e}")
            result_queue.put(None)

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio_data)
            temp_audio_file_path = temp_audio_file.name

        result_queue = Queue()
        transcribe_thread = Thread(
            target=transcribe_worker,
            args=(temp_audio_file_path, result_queue)
        )
        transcribe_thread.start()
        transcribe_thread.join()  # Wait for the thread to complete

        transcription = result_queue.get()
        if transcription is not None:
            logger.info(f"Transcription completed: {transcription}")
        else:
            logger.error("Transcription failed")
            transcription = ""

        return transcription
    except Exception as e:
        logger.error(f"General error in STT: {e}")
        return ""
    finally:
        try:
            os.remove(temp_audio_file_path)
        except Exception as e:
            logger.error(f"Error removing temporary file: {e}")

def stt(audio_data, language=None):
    logger.info(f"Speech-to-text request received. Provider: {stt_config.STT_PROVIDER}")
    
    try:
        if stt_config.STT_PROVIDER == 'openai':
            return stt_openai(audio_data, language)
        elif stt_config.STT_PROVIDER == 'local':
            return stt_local(audio_data, language)
        else:
            logger.error(f"Invalid speech-to-text provider: {stt_config.STT_PROVIDER}")
            raise ValueError(f"Invalid speech-to-text provider: {stt_config.STT_PROVIDER}")
    except Exception as e:
        if "Invalid file format" in str(e):
            logger.error(f"Error in speech-to-text: Invalid audio format. Please ensure the audio is in a supported format.")
        else:
            logger.error(f"Error in speech-to-text: {str(e)}")
        raise
