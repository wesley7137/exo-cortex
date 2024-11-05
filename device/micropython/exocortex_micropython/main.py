from cam import CameraBoard
from comms import Comms
from audio import AudioManager
from wake_word import WakeWordDetector
import time
import os
import json
import asyncio

# Camera ESP32 MAC address (update this with your camera's MAC address)
CAMERA_MAC = b'\x3C\x61\x05\x12\xA4\xBC'

# WebSocket Configuration
WS_SERVER_IP = "192.168.1.238"
WS_PORT = 8005
WS_PATH = "ws/audio"
WS_RECONNECT_MS = 5000

async def handle_audio_stream(wake_word_detector, websocket):
    """Handle continuous audio streaming with wake word detection"""
    while True:
        wake_word_detector.process_audio(websocket)
        await asyncio.sleep_ms(10)

async def handle_esp_now(comms):
    """Handle ESP-NOW communication"""
    while True:
        if comms.esp_now:
            mac, data = comms.esp_now.recv(timeout_ms=100)
            if data:
                try:
                    command = json.loads(data)
                    print(f"Received command from {mac}: {command}")
                    # Handle command here
                except:
                    print(f"Received raw data from {mac}: {data}")
        await asyncio.sleep_ms(100)

async def main():
    try:
        # Initialize camera
        print("Initializing camera...")
        cam = CameraBoard(os)
        cam.cam_init()
        
        # Initialize audio
        print("Initializing audio...")
        audio = AudioManager()
        
        # Initialize wake word detector
        print("Initializing wake word detector...")
        wake_word = WakeWordDetector(audio)
        
        # Initialize communications
        print("Setting up communications...")
        comms = Comms()
        
        # Setup WiFi
        comms.create_wifi_connection('wifi_credentials.json')
        
        # Setup ESP-NOW
        esp_now = comms.create_esp_now_connection()
        esp_now.add_peer(CAMERA_MAC)
        
        # Create WebSocket connection
        print("Setting up WebSocket...")
        WS_ENDPOINT = f'ws://{WS_SERVER_IP}:{WS_PORT}/{WS_PATH}'
        print(f"Connecting to WebSocket: {WS_ENDPOINT}")
        comms.create_rest_connection('audio_ws', WS_ENDPOINT)
        ws = comms.get_rest_connection('audio_ws')
        
        print("Starting main loop...")
        
        # Create tasks
        audio_task = asyncio.create_task(handle_audio_stream(wake_word, ws))
        esp_now_task = asyncio.create_task(handle_esp_now(comms))
        
        # Run tasks
        await asyncio.gather(audio_task, esp_now_task)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
if __name__ == "__main__":
    asyncio.run(main())