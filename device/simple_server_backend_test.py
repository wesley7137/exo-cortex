from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException, WebSocketDisconnect
from fastapi.responses import JSONResponse
from PIL import Image
import io
import os

app = FastAPI()

# Directory to store uploaded images
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected via WebSocket")
    
    try:
        while True:
            try:
                # Receive binary data
                data = await websocket.receive_bytes()
                data_length = len(data)
                print(f"Received audio data: {data_length} bytes")
                
                if data_length > 0:
                    # Save the audio data to a file
                    with open("received_audio.raw", "ab") as audio_file:
                        audio_file.write(data)

                    # Process audio samples
                    samples = [int.from_bytes(data[i:i+4], byteorder='little', signed=True) 
                             for i in range(0, len(data), 4)]
                    
                    if samples:
                        # Calculate average amplitude
                        sum_amplitude = sum(abs((sample >> 14) * 8) for sample in samples)
                        average = sum_amplitude // len(samples)
                        
                        # Map to visual meter (similar to Arduino code)
                        meter = min(50, max(0, int(average * 50 / 2000)))
                        meter = 0 if meter < 2 else meter
                        
                        # Create visual representation
                        meter_visual = "=" * meter
                        print(f"Level: {average} | Audio Level: {meter_visual}")

                    # Send acknowledgment back to the ESP32
                    await websocket.send_text(f"Received {data_length} bytes")
                else:
                    print("Received empty data packet")
                    
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                continue
                
    except WebSocketDisconnect:
        print("Client disconnected normally")
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
    finally:
        await websocket.close()
        print("Client disconnected")
        
# HTTP endpoint for image uploads from ESP32-CAM
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Ensure the file is a JPEG or PNG image
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Load the image from the uploaded file
        image = Image.open(io.BytesIO(await file.read()))

        # Save the image to the uploads directory
        image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        image.save(image_path)
        return JSONResponse(content={"status": "success", "message": "Image uploaded successfully"}, status_code=200)
    
    except Exception as e:
        print(f"Error while processing image: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image")

# Main entry point to run FastAPI with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
