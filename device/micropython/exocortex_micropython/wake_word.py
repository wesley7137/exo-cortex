from machine import I2S, Pin
import time
from micropython import const
import json

# Constants for wake word detection
WAKE_WORD = "hey finn"
CHAT_COMMAND = "let's chat"
STOP_COMMAND = "stop chat"

# Audio thresholds and settings
AUDIO_THRESHOLD = const(2000)  # Adjust based on your microphone sensitivity
SAMPLE_WINDOW_MS = const(500)  # Time window to analyze audio
COMMAND_TIMEOUT_MS = const(5000)  # Time to wait for command after wake word

class WakeWordDetector:
    def __init__(self, audio_manager):
        self.audio = audio_manager
        self.is_listening = False
        self.command_mode = False
        self.last_wake_time = 0
        self.streaming_mode = False
        
        # Command handlers
        self.command_handlers = {
            CHAT_COMMAND: self._handle_chat_command,
            STOP_COMMAND: self._handle_stop_command,
            # Add more commands here
        }
        
    def process_audio(self, websocket=None):
        """Process audio and detect wake word/commands"""
        if not self.audio.i2s:
            return
            
        try:
            # Read audio block
            audio_data = bytearray(self.audio.BLOCK_SIZE * 2)
            num_bytes_read = self.audio.i2s.readinto(audio_data)
            
            if num_bytes_read > 0:
                # Calculate audio level
                max_level = self._calculate_audio_level(audio_data, num_bytes_read)
                
                # If in streaming mode, send audio to websocket
                if self.streaming_mode and websocket and websocket.isConnected():
                    websocket.send_binary(audio_data[:num_bytes_read])
                    return
                
                # Check if audio level exceeds threshold
                if max_level > AUDIO_THRESHOLD:
                    current_time = time.ticks_ms()
                    
                    # If we're waiting for a command
                    if self.command_mode:
                        if time.ticks_diff(current_time, self.last_wake_time) < COMMAND_TIMEOUT_MS:
                            self._process_command(audio_data, num_bytes_read)
                        else:
                            print("Command timeout")
                            self.command_mode = False
                    
                    # Check for wake word
                    elif self._detect_wake_word(audio_data, num_bytes_read):
                        print("Wake word detected!")
                        self.command_mode = True
                        self.last_wake_time = current_time
                        
        except Exception as e:
            print(f"Error processing audio: {e}")
            
    def _calculate_audio_level(self, audio_data, length):
        """Calculate the maximum audio level from the buffer"""
        max_level = 0
        for i in range(0, length, 2):
            sample = int.from_bytes(audio_data[i:i+2], 'little', signed=True)
            max_level = max(max_level, abs(sample))
        return max_level
        
    def _detect_wake_word(self, audio_data, length):
        """Simple energy-based wake word detection"""
        # In a real implementation, you would use a more sophisticated
        # wake word detection algorithm. This is a simplified version.
        energy = sum(abs(int.from_bytes(audio_data[i:i+2], 'little', signed=True))
                    for i in range(0, length, 2)) / (length // 2)
        
        return energy > AUDIO_THRESHOLD
        
    def _process_command(self, audio_data, length):
        """Process command after wake word detection"""
        # In a real implementation, you would use speech-to-text
        # For now, we'll use a simple energy-based detection
        energy = sum(abs(int.from_bytes(audio_data[i:i+2], 'little', signed=True))
                    for i in range(0, length, 2)) / (length // 2)
        
        if energy > AUDIO_THRESHOLD:
            # Simulate command detection
            # In reality, you would use proper speech recognition
            self._handle_chat_command()
            
    def _handle_chat_command(self):
        """Handle the 'let's chat' command"""
        print("Starting chat mode!")
        self.streaming_mode = True
        self.command_mode = False
        
        # Send status message
        status_msg = {
            "type": "status",
            "mode": "chat",
            "status": "started"
        }
        return status_msg
        
    def _handle_stop_command(self):
        """Handle the 'stop chat' command"""
        print("Stopping chat mode!")
        self.streaming_mode = False
        self.command_mode = False
        
        # Send status message
        status_msg = {
            "type": "status",
            "mode": "chat",
            "status": "stopped"
        }
        return status_msg 