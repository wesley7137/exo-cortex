DEVICE_README.md (Updated for New Form Factor)

Project Summary
The ExoCortex device is designed to function as a wearable AI peripheral that acts as a second brain by storing interactions, serving as a knowledge base, and functioning as a memory bank. This AI system includes a local assistant interface with users via voice commands. The peripheral is designed to be worn around the ear, featuring a sleek and minimalistic design for user comfort and seamless integration.
Device Overview:

Form Factor:
The new form factor closely resembles a slim and ergonomic open-ear headset design (as in the images), allowing the device to be worn comfortably for long periods. The main body will house the electronics, including the ESP32 board, battery, microphone, and camera. The design allows the camera to face forward while the components are evenly distributed for balance and comfort.

Main Components:

    ESP32 Board (Main Processing Unit):
        Model: ESP32-WROOM-32
        Dimensions: 25.5mm x 18mm
        Weight: ~4g
        Specs:
            Dual-core Xtensa LX6 processor
            Integrated WiFi 802.11 b/g/n and Bluetooth v4.2 BR/EDR/BLE
            GPIO pins for peripheral integration
            Voltage supply: 3.3V

    Placement:
    The ESP32 will be housed in the rear portion of the headset, near the curved section behind the ear for secure placement. The board will be placed vertically to reduce the device’s width.

    Camera (Wide-Angle, Forward-Facing):
        Model: OV2640 (with a wide-angle lens)
        Dimensions: ~9mm x 9mm
        Specs:
            2MP resolution (1600x1200)
            160-degree wide-angle view
            Interface: SCCB
            Output formats: JPEG, YUV, RGB
        Lens Placement:
        The camera will be flush-mounted on the side of the earpiece, facing forward to capture the user’s viewpoint.

    Microphone (Digital Audio Input):
        Model: Adafruit I2S MEMS Microphone (SPH0645LM4H)
        Dimensions: 6mm x 3mm x 1mm
        Specs:
            I2S (digital audio) interface
            Supply voltage: 1.8V – 3.3V
            Frequency response: 100 Hz – 10 kHz
        Placement:
        The microphone will be integrated into the body of the headset, placed near the front for clear audio capture, with the port facing downward or sideways to minimize noise interference.

    Battery (Power Supply):
        Model: Lithium-ion rechargeable battery
        Capacity: 300-500mAh (based on space availability)
        Voltage: 3.7V nominal
        Dimensions: 25mm x 30mm x 4mm
        Placement:
        The battery will be housed in the rear part of the headset, curving behind the ear for optimal weight distribution. The USB-C charging port will be discreetly placed for easy access.

    Audio Output (Optional Bone Conduction):
        Model: Bone conduction transducer (if integrating audio)
        Dimensions: 20mm x 10mm x 5mm
        Placement:
        If required, the bone conduction transducer will be placed near the bottom portion of the ear hook, allowing sound to be transmitted directly to the user’s ear.

Device Design:

    Earpiece Enclosure Design:
        The enclosure is streamlined to fit behind the ear, with smooth curves to match the shape of the head and ear.
        Materials: Lightweight plastic or composite materials for durability and comfort.
        Weight: The total weight of the device will be kept under 50g to ensure it remains light and wearable for extended periods.

    Forward-Facing Camera:
        The camera module will be embedded on the side of the earpiece near the top, allowing a clear forward-facing view for data capture.
        The camera will sit flush with the housing, minimizing protrusions and maintaining the sleek aesthetic.

    Microphone Port:
        A small opening in the housing near the front will be added for the microphone. The port will be optimized for sound capture while minimizing wind or external noise.

    USB-C Port:
        The USB-C charging port will be located on the inner part of the rear housing, allowing easy access for charging while keeping it hidden from the external view.

Hardware Components:

    ESP32 Placement: Inside the rear housing of the earpiece, with connections routed internally to the camera and microphone.
    Camera Slot: Flush mount on the side, no more than 9mm protrusion.
    Microphone Port: Discreet port near the front to capture clear sound.
    Battery Compartment: Positioned behind the ear for weight distribution.
    Charging Port: USB-C or micro-USB near the back of the device for easy charging.
