import asyncio
import websockets
import json

async def test_connection():
    # Use the full tunneled URL
    uri = "ws://server.build-a-bf.com/ws"  # No need to specify port as it's handled by the tunnel
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")
            
            # Send a test message
            message = {"type": "test", "data": "Hello from test client"}
            await websocket.send(json.dumps(message))
            
            # Wait for response
            response = await websocket.recv()
            print(f"Received response: {response}")
            
    except Exception as e:
        print(f"Connection failed: {e}")
        print(f"Make sure the server is running and the tunnel is active")

# Run the test
if __name__ == "__main__":
    print("Attempting to connect to WebSocket server...")
    asyncio.get_event_loop().run_until_complete(test_connection()) 