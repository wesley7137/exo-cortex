from comms import Comms
import uasyncio as asyncio
from random import randint

def get_sensor_value():
    return randint(0,100)

async def main():
    try:
        # Initialize BLE
        comms = Comms()
        comms.create_ble_connection('19b10000-e8f2-537e-4f6c-d104768a1214', "ESP32")
        
        # Register characteristics
        comms.ble.register_characteristic(
            'sensor', 
            '19b10001-e8f2-537e-4f6c-d104768a1214', 
            read=True, 
            notify=True
        )
        
        # Register services
        comms.ble.register_services()
        
        # Create tasks
        t1 = asyncio.create_task(comms.ble.sensor_task('sensor', get_sensor_value))
        t2 = asyncio.create_task(comms.ble.wait_for_connection())
        
        print("BLE server running. Waiting for connections...")
        await asyncio.gather(t1, t2)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())