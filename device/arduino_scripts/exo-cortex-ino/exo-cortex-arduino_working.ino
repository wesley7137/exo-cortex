#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <HTTPClient.h>

// WiFi credentials
const char* ssid = "17K2.4";
const char* password = "9852587137";

// WebSocket server details
const char* ws_server_url = "server.build-a-bf.com";
const char* ws_path = "/ws";

// BLE Service and Characteristic UUIDs
#define SERVICE_UUID        "12345678-1234-1234-1234-123456789012"
#define CHARACTERISTIC_UUID "87654321-4321-4321-4321-210987654321"

// BLE Server and Characteristic
BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;

// WebSocket client instance
WebSocketsClient webSocket;

#define USE_SERIAL Serial

// Utility function for hex dumps
void hexdump(const void *mem, uint32_t len, uint8_t cols = 16) {
    const uint8_t* src = (const uint8_t*) mem;
    USE_SERIAL.printf("\n[HEXDUMP] Address: 0x%08X len: 0x%X (%d)", (ptrdiff_t)src, len, len);
    for(uint32_t i = 0; i < len; i++) {
        if(i % cols == 0) {
            USE_SERIAL.printf("\n[0x%08X] 0x%08X: ", (ptrdiff_t)src, i);
        }
        USE_SERIAL.printf("%02X ", *src);
        src++;
    }
    USE_SERIAL.printf("\n");
}

// WebSocket event handler
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            USE_SERIAL.printf("[WSc] Disconnected!\n");
            break;
            
        case WStype_CONNECTED:
            USE_SERIAL.printf("[WSc] Connected to url: %s\n", payload);
            // Send initial message
            webSocket.sendTXT("{\"type\":\"hello\",\"client\":\"ESP32\"}");
            break;
            
        case WStype_TEXT:
            USE_SERIAL.printf("[WSc] get text: %s\n", payload);
            // Forward text data to BLE if connected
            if (deviceConnected && pCharacteristic) {
                pCharacteristic->setValue((uint8_t*)payload, length);
                pCharacteristic->notify();
            }
            break;
            
        case WStype_BIN:
            USE_SERIAL.printf("[WSc] get binary length: %u\n", length);
            hexdump(payload, length);
            // Forward binary data to BLE if connected
            if (deviceConnected && pCharacteristic) {
                pCharacteristic->setValue(payload, length);
                pCharacteristic->notify();
            }
            break;
            
        case WStype_ERROR:
            USE_SERIAL.println("[WSc] Error occurred!");
            break;
            
        case WStype_PING:
            USE_SERIAL.println("[WSc] Ping received");
            break;
            
        case WStype_PONG:
            USE_SERIAL.println("[WSc] Pong received");
            break;
            
        default:
            break;
    }
}

// BLE Server Callbacks
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
        USE_SERIAL.println("BLE Client Connected");
    };

    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
        USE_SERIAL.println("BLE Client Disconnected");
    }
};

void initializeBLE() {
    BLEDevice::init("ESP32-S3 BLE Server");
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

    BLEService *pService = pServer->createService(SERVICE_UUID);
    pCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ   |
        BLECharacteristic::PROPERTY_WRITE  |
        BLECharacteristic::PROPERTY_NOTIFY |
        BLECharacteristic::PROPERTY_INDICATE
    );

    pCharacteristic->addDescriptor(new BLE2902());
    pService->start();
    pServer->getAdvertising()->start();
    USE_SERIAL.println("BLE service started, waiting for client connection...");
}

void setup() {
    USE_SERIAL.begin(115200);
    delay(1000);
    
    USE_SERIAL.println("\nStarting ESP32...");

    // Setup WiFi - using direct WiFi.begin(), NOT wifiMulti
    USE_SERIAL.println("Connecting to WiFi...");
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        USE_SERIAL.print(".");
        delay(500);
    }
    USE_SERIAL.println("\nWiFi connected!");
    USE_SERIAL.print("IP Address: ");
    USE_SERIAL.println(WiFi.localIP());

    // Initialize WebSocket connection with domain
    USE_SERIAL.printf("Setting up WebSocket connection to %s%s\n", 
                     ws_server_url, ws_path);
    webSocket.begin(ws_server_url, 80, ws_path);
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);
    webSocket.enableHeartbeat(15000, 3000, 2);

    // Initialize BLE
    initializeBLE();
}

void loop() {
    webSocket.loop();

    // Handle BLE data if connected
    if (deviceConnected && pCharacteristic) {
        String value = pCharacteristic->getValue();
        if (value.length() > 0) {
            USE_SERIAL.printf("Received from BLE client: %s\n", value.c_str());
            webSocket.sendTXT(value.c_str());
        }
    }

    delay(10);  // Small delay to prevent watchdog issues
}