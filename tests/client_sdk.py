import asyncio
import websockets
import aiohttp
import json
import wave
import numpy as np
from datetime import datetime
import logging
from typing import Optional, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioServerClient:
    def __init__(self, host: str = "localhost", port: int = 8005):
        """Initialize the client SDK for the audio server.
        
        Args:
            host (str): Server hostname
            port (int): Server port
        """
        self.base_url = f"http://{host}:{port}"
        self.ws_url = f"ws://{host}:{port}/ws/audio"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_recording = False
        self.on_audio_level: Optional[Callable[[int], None]] = None
        self.on_recording_complete: Optional[Callable[[str], None]] = None
        
    async def connect(self):
        """Establish WebSocket connection with the server."""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            logger.info("WebSocket connection established")
            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def _listen_for_messages(self):
        """Listen for incoming WebSocket messages."""
        while True:
            try:
                if self.websocket:
                    message = await self.websocket.recv()
                    if isinstance(message, str):
                        await self._handle_text_message(message)
                    else:
                        await self._handle_binary_message(message)
            except websockets.exceptions.ConnectionClosed:
                logger.info("WebSocket connection closed")
                break
            except Exception as e:
                logger.error(f"Error in message listener: {e}")
                break

    async def _handle_text_message(self, message: str):
        """Handle incoming text messages."""
        try:
            data = json.loads(message)
            if data.get("type") == "audio_level":
                if self.on_audio_level:
                    self.on_audio_level(data["level"])
            elif data.get("status") == "success" and "filename" in data:
                if self.on_recording_complete:
                    self.on_recording_complete(data["filename"])
        except json.JSONDecodeError:
            logger.error("Failed to parse message as JSON")

    async def _handle_binary_message(self, message: bytes):
        """Handle incoming binary messages."""
        # Implement if server sends binary data
        pass

    async def start_recording(self):
        """Start audio recording."""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "command",
                "command": "start_recording"
            }))
            self.is_recording = True
            logger.info("Recording started")

    async def stop_recording(self):
        """Stop audio recording."""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "command",
                "command": "stop_recording"
            }))
            self.is_recording = False
            logger.info("Recording stopped")

    async def send_audio_data(self, audio_data: bytes):
        """Send audio data to the server."""
        if self.websocket:
            await self.websocket.send(audio_data)

    async def start_complex_chat(self):
        """Start complex chat mode."""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "command",
                "command": "lets_chat"
            }))
            logger.info("Complex chat mode activated")

    async def stop_complex_chat(self):
        """Stop complex chat mode."""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "command",
                "command": "stop_chat"
            }))
            logger.info("Complex chat mode deactivated")

    async def upload_image(self, image_path: str):
        """Upload an image to the server."""
        async with aiohttp.ClientSession() as session:
            with open(image_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file',
                             f,
                             filename=image_path.split('/')[-1],
                             content_type='image/jpeg')
                
                async with session.post(f"{self.base_url}/upload", data=data) as response:
                    result = await response.json()
                    logger.info(f"Image upload result: {result}")
                    return result

    async def check_health(self):
        """Check server health status."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                return await response.json()

    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            logger.info("Connection closed")

# Example usage and test code
async def test_client():
    # Initialize client
    client = AudioServerClient()
    
    # Connect to server
    connected = await client.connect()
    if not connected:
        logger.error("Failed to connect to server")
        return

    # Set up callbacks
    def on_audio_level(level: int):
        logger.info(f"Audio level: {level}")

    def on_recording_complete(filename: str):
        logger.info(f"Recording saved as: {filename}")

    client.on_audio_level = on_audio_level
    client.on_recording_complete = on_recording_complete

    try:
        # Check server health
        health = await client.check_health()
        logger.info(f"Server health: {health}")

        # Start complex chat mode
        await client.start_complex_chat()
        
        # Start recording
        await client.start_recording()

        # Simulate sending audio data
        # Generate 5 seconds of sample audio data
        sample_rate = 16000
        duration = 5  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        
        # Send audio data in chunks
        chunk_size = 1024
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            await client.send_audio_data(chunk.tobytes())
            await asyncio.sleep(0.01)  # Small delay to prevent overwhelming the server

        # Stop recording
        await client.stop_recording()

        # Stop complex chat mode
        await client.stop_complex_chat()

        # Wait a bit for any final messages
        await asyncio.sleep(2)

    finally:
        # Close connection
        await client.close()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_client())