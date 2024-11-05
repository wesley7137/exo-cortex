import asyncio
import threading
import time
import ssl
import logging
import os
import sys
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Configure logging to output to console with timestamp
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS with more restrictive settings
origins = ["*"]  # Be more permissive during testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Buffer to hold received audio data with size limit
MAX_BUFFER_SIZE = 1000
audio_data_buffer = []
buffer_lock = threading.Lock()

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "connect-src 'self' ws: wss:; "
        "img-src 'self'; "
        "style-src 'self'; "
        "font-src 'self'; "
        "object-src 'none'"
    )
    return response

@app.get('/')
def index():
    return "ESP32 Audio Streaming Backend - Status: Running"

@app.get('/health')
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get('/test')
def test_endpoint():
    return {"status": "ok", "message": "ESP32 test endpoint working"}

@app.get('/esp32-test')
def esp32_test():
    return "ESP32 Connection Test - OK", 200

# List to keep track of connected clients
clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    logger.info(f"Client connected: {websocket.client}")
    try:
        while True:
            data = await websocket.receive()
            if 'text' in data:
                text_data = data['text']
                logger.info(f"Received text data: {text_data}")
                # Process text data
                import json
                try:
                    message = json.loads(text_data)
                    if message.get('type') == 'audio_data':
                        audio_data = message.get('data')
                        if audio_data:
                            with buffer_lock:
                                if len(audio_data_buffer) >= MAX_BUFFER_SIZE:
                                    audio_data_buffer.pop(0)
                                audio_data_buffer.append(audio_data)
                            logger.info(f"Received audio data of length: {len(audio_data)}")
                            await websocket.send_json({'event': 'audio_received', 'status': 'success'})
                    else:
                        logger.info(f"Unknown message type: {message.get('type')}")
                except json.JSONDecodeError:
                    logger.error("Failed to decode JSON")
                    await websocket.send_json({'event': 'error', 'message': 'Invalid JSON'})
            elif 'bytes' in data:
                binary_data = data['bytes']
                # Process binary data
                logger.info(f"Received binary data of length: {len(binary_data)}")
                # Store the binary data
                with buffer_lock:
                    if len(audio_data_buffer) >= MAX_BUFFER_SIZE:
                        audio_data_buffer.pop(0)
                    audio_data_buffer.append(binary_data)
                await websocket.send_text('Binary data received')
    except WebSocketDisconnect:
        clients.remove(websocket)
        logger.info(f"Client disconnected: {websocket.client}")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        await websocket.close()

# Function to stream audio data to clients
async def stream_audio_to_clients():
    while True:
        if audio_data_buffer:
            with buffer_lock:
                audio_chunk = audio_data_buffer.pop(0)
            for client in clients:
                try:
                    await client.send_bytes(audio_chunk)
                    logger.debug("Sent audio data to client")
                except Exception as e:
                    logger.error(f"Error sending data to client: {e}")
        await asyncio.sleep(0.1)

# Start background task for streaming audio
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(stream_audio_to_clients())

# SSL context (if needed)
def create_ssl_context():
    """Create SSL context if certificates exist, otherwise return None"""
    cert_path = 'cert.pem'
    key_path = 'key.pem'
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            certfile=cert_path,
            keyfile=key_path
        )
        return ssl_context
    return None

if __name__ == '__main__':
    import uvicorn
    
    cert_path = 'cert.pem'
    key_path = 'key.pem'
    
    # Check if SSL certificates exist
    if os.path.exists(cert_path) and os.path.exists(key_path):
        uvicorn.run(
            app,
            host='0.0.0.0',
            port=5005,
            ssl_keyfile=key_path,
            ssl_certfile=cert_path,
            log_level="debug",
            reload=True,
        )
    else:
        # Run without SSL if certificates don't exist
        uvicorn.run(
            app,
            host='0.0.0.0',
            port=5005,
            log_level="debug",
            reload=True,
        )
