from machine import I2S, Pin
import time
from comms import Comms
import json

class AudioManager:
    def __init__(self):
        # I2S Configuration
        self.I2S_WS_PIN = 42    # Word Select (LRC) pin
        self.I2S_SD_PIN = 41    # Serial Data (DOUT) pin
        self.I2S_SCK_PIN = -1   # Serial Clock (BCLK) pin not used for PDM
        
        # Audio settings
        self.SAMPLE_RATE = 16000
        self.BITS = 16
        self.CHANNELS = 1
        self.BLOCK_SIZE = 1024
        
        # Recording settings
        self.RECORDING_SECONDS = 5
        self.BUFFER_SIZE = self.SAMPLE_RATE * self.RECORDING_SECONDS * (self.BITS // 8) * self.CHANNELS
        self.recording_buffer = bytearray(self.BUFFER_SIZE)
        self.buffer_index = 0
        
        # State flags
        self.is_recording = False
        self.recording_start_time = 0
        self.complex_task_mode = False
        
        # Initialize I2S
        self.i2s = None
        self.init_i2s()
        
    def init_i2s(self):
        """Initialize I2S for the PDM microphone"""
        try:
            # Configure I2S for PDM microphone
            self.i2s = I2S(
                0,                          # I2S ID
                sck=Pin(self.I2S_SCK_PIN), # Serial clock
                ws=Pin(self.I2S_WS_PIN),   # Word select
                sd=Pin(self.I2S_SD_PIN),   # Serial data
                mode=I2S.RX,               # Receive mode
                bits=self.BITS,            # Sample bits
                format=I2S.MONO,           # Mono format
                rate=self.SAMPLE_RATE,     # Sample rate
                ibuf=self.BLOCK_SIZE       # Input buffer size
            )
            print("I2S initialized successfully")
        except Exception as e:
            print(f"Failed to initialize I2S: {e}")
            
    def read_microphone(self, websocket=None):
        """Read microphone data and optionally send to WebSocket"""
        if not self.i2s:
            return
        
        try:
            # Read audio block
            audio_data = bytearray(self.BLOCK_SIZE * 2)  # 2 bytes per sample
            num_bytes_read = self.i2s.readinto(audio_data)
            
            if num_bytes_read > 0:
                # Calculate audio level for debugging
                max_value = 0
                for i in range(0, num_bytes_read, 2):
                    # Convert bytes to 16-bit sample
                    sample = int.from_bytes(audio_data[i:i+2], 'little', signed=True)
                    max_value = max(max_value, abs(sample))
                
                # Print audio level every second
                current_time = time.ticks_ms()
                if not hasattr(self, 'last_print_time') or time.ticks_diff(current_time, self.last_print_time) >= 1000:
                    print(f"Audio Level: {max_value}")
                    self.last_print_time = current_time
                
                # If recording, store in buffer
                if self.is_recording and self.buffer_index < len(self.recording_buffer):
                    bytes_to_copy = min(num_bytes_read, len(self.recording_buffer) - self.buffer_index)
                    self.recording_buffer[self.buffer_index:self.buffer_index + bytes_to_copy] = audio_data[:bytes_to_copy]
                    self.buffer_index += bytes_to_copy
                
                # If websocket is connected, send the audio data
                if websocket and websocket.isConnected():
                    websocket.send_binary(audio_data[:num_bytes_read])
                
        except Exception as e:
            print(f"Error reading microphone: {e}")
            
    def start_recording(self):
        """Start audio recording"""
        if self.is_recording:
            print("Already recording!")
            return
            
        self.buffer_index = 0
        self.is_recording = True
        self.recording_start_time = time.ticks_ms()
        print("Recording started...")
        
    def save_recording(self, websocket=None):
        """Save recording and optionally send via WebSocket"""
        if not self.is_recording or self.buffer_index == 0:
            print("No recording to save!")
            return
            
        if websocket and websocket.isConnected():
            # Send recording complete message
            status_msg = {
                "type": "recording",
                "status": "complete",
                "samples": self.buffer_index
            }
            websocket.send_text(json.dumps(status_msg))
            
            # Send audio data in chunks
            CHUNK_SIZE = 1024
            for i in range(0, self.buffer_index, CHUNK_SIZE):
                chunk = self.recording_buffer[i:min(i + CHUNK_SIZE, self.buffer_index)]
                websocket.send_binary(chunk)
                time.sleep_ms(10)  # Small delay to prevent overwhelming the WebSocket
                
        # Reset recording state
        self.buffer_index = 0
        self.is_recording = False
        print("Recording complete and sent to server") 