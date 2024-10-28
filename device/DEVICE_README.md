DEVICE_README.md (Updated for New Form Factor)

Project Summary
The ExoCortex device is designed to function as a wearable AI peripheral that acts as a second brain by storing interactions, serving as a knowledge base, and functioning as a memory bank. This AI system includes a local assistant interface with users via voice commands. The peripheral is designed to be worn around the ear, featuring a sleek and minimalistic design for user comfort and seamless integration.
Device Overview:

Form Factor:
The new form factor closely resembles a slim and ergonomic bone conduction headset design (as in the images), allowing the device to be worn comfortably for long periods. The main body will house the electronics, including the ESP32 board, battery, microphone, and camera. The design allows the camera to face forward while the components are evenly distributed for balance and comfort.

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

DESIGN CONCEPTS VERSION 1:

The headset design is based on a bone conduction ergonomic form factor, offering a sleek, lightweight frame for all-day comfort. The main frame is made from flexible, durable material that curves gently to conform to the user’s head, similar to the shape of high-end sports bone conduction headphones.

Frame: The headband is a smooth, slim structure with rounded edges for an unobtrusive profile. It is slightly thicker at the back, allowing the weight to be evenly distributed. The frame curves around the ears, leaving them free, while the rest of the band wraps around the back of the head for stability.

Ear Sections: The ear rests are cuboid-shaped and slightly thicker than the main band to house small components such as the battery and microphone. These cuboids are sleek, with rounded edges to avoid discomfort and ensure the overall design appears flush against the headband. The ear section features subtle ergonomic angling, making sure it rests snugly above the ear without slipping.

Components Housing: The device will house electronics such as an ESP32 board, battery, microphone, and camera. The housing is located mostly behind the ears, ensuring that the weight is distributed without causing strain. The electronics are encased within the cuboid structures near the ears, with a microphone embedded near the mouth area and a camera placed discreetly on the front section, pointing forward.

Camera Placement: The forward-facing camera is subtly embedded in the front area of the headband, allowing for clear recording or capturing of visuals. The camera’s design seamlessly blends into the overall frame without protrusion, making it almost invisible when not in use.

Button Integration: Discreet control buttons are located on one side of the device, allowing for easy access to power, volume control, and other functional elements without detracting from the sleek, minimalist design.

Balance and Comfort: The internal components are evenly distributed across both sides of the frame for balance. This avoids pressure points on the ears or back of the head. The device is light enough for prolonged use, with slightly thicker sections behind the ears to stabilize and counterbalance the camera at the front.

DESIGN CONCEPTS VERSION 2:
Description:
The design now shifts to a side-mounted electronics housing connected via an elastic band that wraps around the head, similar to the way headlamps or certain sports headsets are worn. The main electronic components (ESP32, battery, microphone, camera) are housed in a slim, sleek side piece. This side housing includes an earpiece integrated into the design, which rests over or near one ear for balanced weight distribution and functionality. The camera would protrude slightly from this housing, allowing forward-facing visuals while the other components are comfortably fitted in the same enclosure.

The elastic band keeps the device secure and comfortable around the head without the need for a full 3D-printed headband. This setup not only simplifies production but also increases flexibility, as users can adjust the fit to their head size. The slim side-mounted housing ensures the device is less obtrusive and lightweight, making it ideal for long-term wear.

Looking at your shopping cart and components list, you have:

    Ferwooh 6PCS Mini Breadboard Kit with jumper cables
    Heat shrink tubing kit
    HiLetgo CP2102 USB to TTL Module
    DORHEA ESP32-CAM board with OV2640 camera
    PowerBoost 1000C (already owned)
    OV2640 camera module 75-degree wide angle (already owned)
    Lithium ion battery (already owned)
    I2S MEMS Microphone (already owned)
    Bluetooth LE module (already owned)
    Small speakers (already owned)

For your Google Glass-style headpiece project, you have all the essential components. The only additional items you might want to consider are:
Optional but Useful

    Small zip ties for cable management
    Double-sided tape or mounting adhesive
    Kapton tape for insulating components
    Small screwdriver set for any adjustments

Component Placement
Camera Module (OV2640-75MM)

    Position at front/temple area
    Use the 75mm flex cable to route behind the ear
    Angle slightly downward for natural field of view

ESP32 Board

    Place behind the ear where the temple piece widens
    This provides more surface area for mounting
    Helps balance weight distribution

Power/Charging

    PowerBoost 1000C near ESP32
    USB charging port positioned at bottom/rear of temple piece
    Easy access for charging while device is off

Audio Components

    Speaker

    Position near but not directly on ear
    Angle toward ear canal
    Consider bone conduction placement option

    MEMS Microphone

    Place near mouth/jaw area
    Keep away from speaker to prevent feedback
    Angle toward mouth for better voice capture

Design Considerations

    Route flex cables and wires through temple piece interior
    Add ventilation holes for heat dissipation near ESP32
    Include small LED status indicators visible to user
    Consider making temple piece slightly wider to accommodate components
    Use heat shrink tubing for wire management
    Add strain relief for charging port
