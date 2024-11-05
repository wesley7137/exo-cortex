import wave
import os
import glob

# Audio parameters matching your ESP32 configuration
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit audio = 2 bytes
SAMPLE_RATE = 16000

def convert_raw_to_wav(raw_file):
    # Create WAV filename from RAW filename
    wav_file = raw_file.replace('.raw', '.wav')
    
    # Read raw audio data
    with open(raw_file, 'rb') as rf:
        raw_data = rf.read()
    
    # Create WAV file
    with wave.open(wav_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(raw_data)
    
    print(f"Converted {raw_file} to {wav_file}")

def main():
    # Convert all .raw files in the audio directory
    raw_files = glob.glob('audio/*.raw')
    for raw_file in raw_files:
        convert_raw_to_wav(raw_file)

if __name__ == "__main__":
    main() 