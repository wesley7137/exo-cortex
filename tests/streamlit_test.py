import streamlit as st
import asyncio
from client_sdk import AudioServerClient
import sounddevice as sd
import numpy as np
import queue
import threading
from datetime import datetime
import time
import os
from PIL import Image
from threading import Lock
import streamlit.runtime.scriptrunner as scriptrunner

# Initialize all session state variables in a function
def init_session_state():
    if 'client' not in st.session_state:
        st.session_state.client = None
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'complex_mode' not in st.session_state:
        st.session_state.complex_mode = False
    if 'audio_queue' not in st.session_state:
        st.session_state.audio_queue = queue.Queue()
    if 'audio_level' not in st.session_state:
        st.session_state.audio_level = 0
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []
    if 'stream' not in st.session_state:
        st.session_state.stream = None

# Call initialization function at the start
init_session_state()

# Add a thread lock
state_lock = Lock()

st.title("🎤 Audio Server Test Interface")

# Server Connection Settings
st.sidebar.header("Server Settings")
host = st.sidebar.text_input("Server Host", "localhost")
port = st.sidebar.number_input("Server Port", value=8005, min_value=1, max_value=65535)

async def connect_to_server():
    if hasattr(st.session_state, 'client') and st.session_state.client:
        await st.session_state.client.close()
    
    client = AudioServerClient(host=host, port=port)
    connected = await client.connect()
    
    if connected:
        st.session_state.client = client
        return True
    return False

def audio_callback(indata, frames, time, status):
    """Callback for sounddevice to handle audio input"""
    if status:
        print(status)
    
    with state_lock:
        if hasattr(st.session_state, 'recording') and st.session_state.recording:
            st.session_state.audio_queue.put(indata.copy())

# Connection status and control
col1, col2 = st.columns(2)
with col1:
    if st.button("Connect to Server"):
        with st.spinner("Connecting..."):
            if asyncio.run(connect_to_server()):
                st.success("Connected!")
            else:
                st.error("Connection failed!")

with col2:
    if st.button("Check Server Health"):
        if st.session_state.client:
            with st.spinner("Checking..."):
                health = asyncio.run(st.session_state.client.check_health())
                st.json(health)
        else:
            st.warning("Please connect to server first")

# Audio Recording Section
st.header("🎙️ Audio Recording")

col3, col4 = st.columns(2)
with col3:
    if st.button("Start Recording" if not st.session_state.recording else "Stop Recording"):
        if st.session_state.client:
            with state_lock:
                if not st.session_state.recording:
                    # Start recording
                    st.session_state.recording = True
                    asyncio.run(st.session_state.client.start_recording())
                    
                    # Start audio input stream
                    stream = sd.InputStream(
                        channels=1,
                        samplerate=16000,
                        callback=audio_callback
                    )
                    stream.start()
                    st.session_state.stream = stream
                else:
                    # Stop recording
                    st.session_state.recording = False
                    st.session_state.stream.stop()
                    st.session_state.stream.close()
                    asyncio.run(st.session_state.client.stop_recording())
        else:
            st.warning("Please connect to server first")

# Create a placeholder for the audio level display
audio_level_placeholder = st.empty()

# Function to update audio level display
def update_audio_level():
    ctx = streamlit.runtime.scriptrunner.get_script_run_ctx()
    
    def _update():
        while True:
            try:
                if ctx:
                    streamlit.runtime.scriptrunner.add_script_run_ctx(ctx)
                
                with state_lock:
                    level = st.session_state.audio_level
                try:
                    audio_level_placeholder.metric("Audio Level", f"{level} dB")
                except Exception as e:
                    print(f"Error updating audio level: {e}")
            except Exception as e:
                print(f"Error in audio level update: {e}")
            finally:
                time.sleep(0.1)
    
    thread = threading.Thread(target=_update, daemon=True)
    thread.start()
    return thread

# Start the audio level update thread
level_thread = threading.Thread(target=update_audio_level, daemon=True)
level_thread.start()

# Complex Chat Mode
st.header("💭 Complex Chat Mode")
col5, col6 = st.columns(2)
with col5:
    if st.button("Start Complex Chat" if not st.session_state.complex_mode else "Stop Complex Chat"):
        if st.session_state.client:
            if not st.session_state.complex_mode:
                asyncio.run(st.session_state.client.start_complex_chat())
                st.session_state.complex_mode = True
            else:
                asyncio.run(st.session_state.client.stop_complex_chat())
                st.session_state.complex_mode = False
        else:
            st.warning("Please connect to server first")

# Image Upload Section
st.header("📸 Image Upload")
uploaded_file = st.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png'])
if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    # Save temporarily and upload
    if st.button("Upload Image"):
        if st.session_state.client:
            with st.spinner("Uploading..."):
                # Save temporary file
                temp_path = f"temp_{int(time.time())}.jpg"
                image.save(temp_path)
                
                # Upload
                try:
                    result = asyncio.run(st.session_state.client.upload_image(temp_path))
                    st.json(result)
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        else:
            st.warning("Please connect to server first")

# Audio Visualization
st.header("📊 Audio Visualization")
chart = st.empty()

# Background task to update audio visualization
def update_audio_viz():
    # Get the current script run context
    ctx = streamlit.runtime.scriptrunner.get_script_run_ctx()
    
    def _update():
        while True:
            try:
                # Set the script context for this thread
                if ctx:
                    streamlit.runtime.scriptrunner.add_script_run_ctx(ctx)
                
                with state_lock:
                    if not hasattr(st.session_state, 'recording'):
                        time.sleep(0.1)
                        continue
                        
                    is_recording = st.session_state.recording
                    audio_queue = getattr(st.session_state, 'audio_queue', None)
                    client = getattr(st.session_state, 'client', None)

                if is_recording and audio_queue and not audio_queue.empty():
                    audio_data = audio_queue.get()
                    level = int(np.abs(audio_data).mean() * 1000)
                    
                    with state_lock:
                        st.session_state.audio_level = level
                    
                    if client:
                        try:
                            asyncio.run(client.send_audio_data(audio_data.tobytes()))
                        except Exception as e:
                            print(f"Error sending audio data: {e}")
                            
            except Exception as e:
                print(f"Error in audio visualization: {e}")
            finally:
                time.sleep(0.1)
    
    # Start the update thread with the context
    thread = threading.Thread(target=_update, daemon=True)
    thread.start()
    return thread

# Start background thread for audio visualization
viz_thread = threading.Thread(target=update_audio_viz, daemon=True)
viz_thread.start()

# Status and Logs Section
st.header("📝 Status and Logs")
log_container = st.empty()

def update_log(message):
    current_log = log_container.text_area("Activity Log", height=200, value=message)

# Cleanup on app close
def cleanup():
    try:
        with state_lock:
            if hasattr(st.session_state, 'client') and st.session_state.client:
                asyncio.run(st.session_state.client.close())
            if hasattr(st.session_state, 'stream') and st.session_state.stream:
                st.session_state.stream.stop()
                st.session_state.stream.close()
            # Set flags to stop threads
            st.session_state.recording = False
            st.session_state.complex_mode = False
    except Exception as e:
        print(f"Cleanup error: {e}")

# Register cleanup
import atexit
atexit.register(cleanup)