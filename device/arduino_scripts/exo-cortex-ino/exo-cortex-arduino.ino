#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <HTTPClient.h>
#include "esp_afe_sr_iface.h"
#include "esp_afe_sr_models.h"
#include <ESP_I2S.h>

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

// Modify the I2S pin definitions to match XIAO ESP32-S3 Sense
#define I2S_WS_PIN 42  // PDM Clock
#define I2S_SD_PIN 41  // PDM Data
#define I2S_PORT I2S_NUM_0

// Function to initialize I2S for XIAO ESP32-S3 Sense
void initializeI2S() {
    // Configure I2S for PDM microphone
    I2S.setPinsPdmRx(I2S_WS_PIN, I2S_SD_PIN);
    
    // Initialize I2S with PDM mode
    if (!I2S.begin(I2S_MODE_PDM_RX, 16000, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO)) {
        USE_SERIAL.println("Failed to initialize I2S!");
        while (1); // do nothing
    }
}

// AFE configuration
static esp_afe_sr_iface_t *afe_handle = NULL;
static esp_afe_sr_data_t *afe_data = NULL;
static int audio_chunksize;
static int16_t *audio_buffer = NULL;
static bool is_recording = false;

// Function to initialize AFE
void initializeAFE() {
    afe_handle = &ESP_AFE_SR_HANDLE;
    afe_config_t afe_config = AFE_CONFIG_DEFAULT();
    
    // Configure AFE
    afe_config.aec_init = false;        // Disable AEC since we don't need echo cancellation
    afe_config.se_init = true;          // Enable noise suppression
    afe_config.vad_init = true;         // Enable Voice Activity Detection
    afe_config.wakenet_init = true;     // Enable wake word detection
    afe_config.voice_communication_init = false;
    afe_config.wakenet_model_name = "wn9_hilexin";  // Use "Hi Lexin" as wake word
    afe_config.wakenet_mode = DET_MODE_90;          // Single channel mode
    afe_config.afe_mode = SR_MODE_LOW_COST;
    afe_config.pcm_config.total_ch_num = 1;
    afe_config.pcm_config.mic_num = 1;
    afe_config.pcm_config.ref_num = 0;

    // Create AFE instance
    afe_data = afe_handle->create_from_config(&afe_config);
    if (!afe_data) {
        USE_SERIAL.println("Failed to create AFE instance");
        return;
    }

    // Get the required audio chunk size
    audio_chunksize = afe_handle->get_feed_chunksize(afe_data);
    audio_buffer = (int16_t*)malloc(audio_chunksize * sizeof(int16_t));
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

    // Initialize AFE and I2S
    initializeAFE();
    initializeI2S();
}

void loop() {
    webSocket.loop();

    // Handle audio processing
    if (is_recording) {
        int sample = I2S.read();
        
        if (sample && sample != -1 && sample != 1) {
            // Feed audio data to AFE
            if (audio_buffer != nullptr) {
                audio_buffer[0] = sample;
                afe_handle->feed(afe_data, audio_buffer);
                
                // Fetch processed audio
                afe_fetch_result_t *fetch_result = afe_handle->fetch(afe_data);
                
                if (fetch_result) {
                    // Check for wake word
                    if (fetch_result->wakeup_state == WAKENET_DETECTED) {
                        USE_SERIAL.println("Wake word detected!");
                        // Send wake word detection event to server
                        webSocket.sendTXT("{\"type\":\"wake_word_detected\"}");
                    }
                    
                    // Check for voice commands
                    if (fetch_result->vad_state == VAD_SPEECH) {
                        // Send audio data to server
                        webSocket.sendBIN((uint8_t*)fetch_result->data, fetch_result->data_size);
                    }
                }
            }
        }
    }

    // Handle BLE data if connected
    if (deviceConnected && pCharacteristic) {
        String value = pCharacteristic->getValue();
        if (value.length() > 0) {
            USE_SERIAL.printf("Received from BLE client: %s\n", value.c_str());
            
            // Handle voice commands
            if (value == "start_recording") {
                is_recording = true;
                USE_SERIAL.println("Started recording");
            } else if (value == "stop_recording") {
                is_recording = false;
                USE_SERIAL.println("Stopped recording");
            }
            
            webSocket.sendTXT(value.c_str());
        }
    }

    delay(10);  // Small delay to prevent watchdog issues
}