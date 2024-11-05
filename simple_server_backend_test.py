from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
import logging
import uvicorn
import json
import wave
import numpy as np
from io import BytesIO
import websockets
from fastapi_middleware_logger import FastAPIMiddleWareLogger
import logging

print("Starting server initialization...")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("Creating FastAPI application...")
logging.basicConfig(level=logging.INFO)
app = FastAPIMiddleWareLogger()  # Instead of FastAPI()

@app.get("/")
def get_index():
    return {"status": "ok"}

print("Configuring CORS middleware...")
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Creating required directories...")
# Create directories if they don't exist
UPLOAD_DIR = "uploads"
AUDIO_DIR = "audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
print(f"Created directories: {UPLOAD_DIR}, {AUDIO_DIR}")

# Store active WebSocket connections
active_connections = []

RECORDING_LENGTH_SECONDS = 5
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit audio = 2 bytes

print(f"Audio settings configured - Sample Rate: {SAMPLE_RATE}Hz, Channels: {CHANNELS}, Sample Width: {SAMPLE_WIDTH} bytes")
# ... existing imports and setup ...

# Add these constants at the top with other configurations
WAKE_WORD = "hey finn"
COMPLEX_TASK_TRIGGER = "let's chat"
STOP_COMMAND = "stop chat"

# Add this new class for wake word and command handling
class AudioProcessor:
    def __init__(self):
        self.is_listening = False
        self.in_complex_mode = False
        
    async def process_audio(self, audio_data, websocket):
        # Convert audio data to text using whisper or similar
        # This is a placeholder - you'll need to add actual speech recognition
        try:
            # Convert numpy array to audio and recognize
            samples = np.frombuffer(audio_data, dtype=np.int16)
            
            # TODO: Add actual speech recognition here
            # For now, just print audio levels for debugging
            max_level = np.max(np.abs(samples))
            if max_level > 1000:  # Adjust threshold as needed
                logger.info(f"Significant audio detected - Level: {max_level}")
                
                # Send feedback to client
                await websocket.send_json({
                    "type": "audio_level",
                    "level": int(max_level)
                })
                
                # If we detect significant audio and we're not in complex mode,
                # start recording for command processing
                if not self.in_complex_mode and max_level > 5000:  # Adjust threshold
                    await websocket.send_json({
                        "type": "command",
                        "command": "start_recording"
                    })
        
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    print("New WebSocket connection request received")
    await websocket.accept()
    active_connections.append(websocket)
    audio_recorder = AudioRecorder()
    audio_processor = AudioProcessor()
    logger.info("Audio WebSocket client connected")
    
    try:
        while True:
            try:
                # Use receive() to handle both text and binary messages
                message = await websocket.receive()
                
                if message["type"] == "websocket.disconnect":
                    logger.info("Client initiated disconnect")
                    break
                    
                elif message["type"] == "websocket.receive":
                    if "text" in message:
                        # Handle text messages
                        data = message["text"]
                        try:
                            command = json.loads(data)
                            if command.get("type") == "command":
                                cmd = command.get("command")
                                if cmd == "lets_chat":
                                    audio_processor.in_complex_mode = True
                                    await websocket.send_json({
                                        "status": "success",
                                        "message": "Complex task mode activated"
                                    })
                                elif cmd == "stop_chat":
                                    audio_processor.in_complex_mode = False
                                    await websocket.send_json({
                                        "status": "success",
                                        "message": "Complex task mode deactivated"
                                    })
                                elif cmd == "start_recording":
                                    audio_recorder.start_recording()
                                    await websocket.send_json({
                                        "status": "success",
                                        "message": "Recording started"
                                    })
                        except json.JSONDecodeError:
                            logger.warning("Received invalid JSON")
                            
                    elif "bytes" in message:
                        # Handle binary audio data
                        data = message["bytes"]
                        await audio_processor.process_audio(data, websocket)
                        
                        if audio_recorder.recording:
                            if audio_recorder.add_audio(data):
                                filename = audio_recorder.save_recording()
                                if filename:
                                    await websocket.send_json({
                                        "status": "success",
                                        "message": "Recording saved",
                                        "filename": filename
                                    })
                
            except websockets.exceptions.ConnectionClosedOK:
                logger.info("WebSocket connection closed normally")
                break
                
            except websockets.exceptions.ConnectionClosedError:
                logger.error("WebSocket connection closed with error")
                break
                
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {str(e)}")
                # Don't break here - allow the connection to continue if possible
                continue
                
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info("Client disconnected, cleanup complete")

class AudioRecorder:
    def __init__(self):
        print("Initializing new AudioRecorder instance...")
        self.buffer = BytesIO()
        self.recording = False
        self.samples_collected = 0
        self.expected_samples = RECORDING_LENGTH_SECONDS * SAMPLE_RATE
        self.start_time = None

    def add_audio(self, audio_data):
        if not self.recording:
            print("Received audio data but not recording")
            return False
        
        self.buffer.write(audio_data)
        # Each sample is 2 bytes (16-bit audio)
        samples_added = len(audio_data) // 2
        self.samples_collected += samples_added
        
        # Log progress
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"Recording progress - Time: {elapsed:.1f}s, Samples: {self.samples_collected}/{self.expected_samples}")
        logger.info(f"Recording progress - Time: {elapsed:.1f}s, Samples: {self.samples_collected}/{self.expected_samples}")
        
        # Only complete if we have enough samples AND at least 5 seconds have passed
        if self.samples_collected >= self.expected_samples and elapsed >= RECORDING_LENGTH_SECONDS:
            print("Recording complete - sufficient samples collected")
            return True
        return False

    def start_recording(self):
        print("Starting new audio recording session...")
        self.buffer = BytesIO()
        self.recording = True
        self.samples_collected = 0
        self.start_time = datetime.now()
        logger.info("Started new recording")
    def save_recording(self):
        if not self.buffer.tell():
            print("Warning: Attempted to save empty recording")
            logger.warning("No audio data to save")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{timestamp}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        print(f"Saving recording to {filepath}")
        # Get the buffer value before closing
        audio_data = self.buffer.getvalue()
        
        # Create WAV file
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(SAMPLE_WIDTH)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio_data)
        
        print(f"Successfully saved {len(audio_data)} bytes of audio data")
        logger.info(f"Saved {len(audio_data)} bytes to {filename}")
        
        self.recording = False
        self.buffer = BytesIO()
        return filename

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    print("New WebSocket connection request received")
    await websocket.accept()
    active_connections.append(websocket)
    audio_recorder = AudioRecorder()
    logger.info("Audio WebSocket client connected")
    print(f"WebSocket client connected. Total active connections: {len(active_connections)}")
    bytes_received = 0  # Add counter for received data
    
    try:
        while True:
            try:
                # Try to receive as text first (for JSON commands)
                try:
                    data = await websocket.receive_text()
                    try:
                        command = json.loads(data)
                        print(f"Received command: {command}")
                        logger.info(f"Received command: {command}")
                        
                        if command.get("type") == "command":
                            cmd = command.get("command")
                            if cmd == "start_recording":
                                print("Starting new 5-second recording session")
                                logger.info("Starting 5-second recording")
                                audio_recorder.start_recording()
                                await websocket.send_json({
                                    "status": "success",
                                    "message": "Recording started"
                                })
                            elif cmd == "lets_chat":
                                print("Initiating complex task interaction")
                                logger.info("Starting complex task interaction")
                                await websocket.send_json({
                                    "status": "success",
                                    "message": "Complex task mode activated"
                                })
                            elif cmd == "capture_image":
                                print("Processing image capture request")
                                logger.info("Image capture requested")
                                await websocket.send_json({
                                    "status": "success",
                                    "message": "Image capture requested"
                                })
                            elif cmd == "stop_chat":
                                print("Ending complex task interaction")
                                logger.info("Ending complex task interaction")
                                await websocket.send_json({
                                    "status": "success",
                                    "message": "Complex task mode deactivated"
                                })
                    
                    except json.JSONDecodeError:
                        print("Received non-JSON text data")
                        logger.info("Received text data")
                
                except websockets.exceptions.ConnectionClosedOK:
                    print("WebSocket connection closed normally")
                    logger.info("WebSocket closed normally")
                    break
                except websockets.exceptions.ConnectionClosedError:
                    print("WebSocket connection closed with error")
                    logger.info("WebSocket closed with error")
                    break
                
            except Exception as e:
                # If receive_text fails, try receiving as binary
                try:
                    data = await websocket.receive_bytes()
                    bytes_received += len(data)
                    
                    # Log every second
                    if bytes_received % 16000 == 0:  # Roughly every second
                        print(f"Audio data received - Current chunk: {len(data)} bytes, Total: {bytes_received} bytes")
                        logger.info(f"Received audio data - Size: {len(data)} bytes, "
                                  f"Total received: {bytes_received} bytes")
                        # Also log audio levels
                        samples = np.frombuffer(data, dtype=np.int16)
                        max_level = np.max(np.abs(samples))
                        print(f"Current audio levels - Max amplitude: {max_level}")
                        logger.info(f"Audio level - Max: {max_level}")
                    
                    if audio_recorder.recording:
                        if audio_recorder.add_audio(data):
                            filename = audio_recorder.save_recording()
                            if filename:
                                print(f"Recording completed and saved as {filename}")
                                logger.info(f"Successfully saved recording: {filename}")
                                await websocket.send_json({
                                    "status": "success",
                                    "message": "Recording saved",
                                    "filename": filename
                                })
                                audio_recorder.recording = False
                            else:
                                print("Error: Failed to save recording")
                                logger.error("Failed to save recording")
                    else:
                        # Save as WAV file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        wav_path = os.path.join(AUDIO_DIR, f"audio_{timestamp}.wav")
                        print(f"Saving audio chunk to {wav_path}")
                        
                        with wave.open(wav_path, 'wb') as wav_file:
                            wav_file.setnchannels(CHANNELS)
                            wav_file.setsampwidth(SAMPLE_WIDTH)
                            wav_file.setframerate(SAMPLE_RATE)
                            wav_file.writeframes(data)
                            print(f"Successfully saved audio chunk of {len(data)} bytes")
                            logger.info(f"Saved audio chunk to {wav_path}")
                except websockets.exceptions.ConnectionClosedOK:
                    print("WebSocket connection closed normally during binary transfer")
                    logger.info("WebSocket closed normally")
                    break

                except websockets.exceptions.ConnectionClosedError:
                    print("WebSocket connection closed with error during binary transfer")
                    logger.error("WebSocket closed with error")
                    break

                except Exception as e:
                    print(f"Error processing binary data: {str(e)}")
                    logger.error(f"Error handling binary data: {str(e)}")
                    logger.error(f"Error type: {type(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue

    except Exception as e:
        print(f"WebSocket error occurred: {str(e)}")
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
            print(f"Client disconnected. Remaining connections: {len(active_connections)}")
        logger.info("Audio client disconnected")

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    print(f"Received image upload request: {file.filename}")
    try:
        # Ensure it's an image file
        if not file.content_type.startswith("image/"):
            print(f"Invalid file type received: {file.content_type}")
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "File must be an image"
                },
                status_code=400
            )
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        print(f"Saving image to {filepath}")
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"Successfully saved image: {filename} ({len(content)} bytes)")
        logger.info(f"Image saved successfully: {filename}")
        
        # Notify all audio clients about the new image
        print(f"Notifying {len(active_connections)} connected clients about new image")
        for connection in active_connections:
            try:
                await connection.send_json({
                    "type": "image_uploaded",
                    "filename": filename
                })
            except Exception as e:
                print(f"Failed to notify client about new image: {str(e)}")
                logger.error(f"Error notifying client: {str(e)}")
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Image uploaded successfully",
                "filename": filename
            },
            status_code=200
        )
    
    except Exception as e:
        print(f"Error during image upload: {str(e)}")
        logger.error(f"Error uploading image: {str(e)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Failed to upload image: {str(e)}"
            },
            status_code=500
        )

@app.get("/health")
async def health_check():
    print("Health check endpoint accessed")
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting server on http://0.0.0.0:8005")
    uvicorn.run(app, host="0.0.0.0", port=8005)
