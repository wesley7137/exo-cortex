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
const char* ws_server_url = "192.168.1.254";
const uint16_t ws_server_port = 5005;
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

// Add connection state tracking at the top of the file, before it's used
bool wsConnected = false;
unsigned long lastConnectionAttempt = 0;
const unsigned long connectionTimeout = 10000; // 10 seconds timeout

// WebSocket event handler with enhanced debugging
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("WebSocket Disconnected");
            wsConnected = false;
            Serial.println("Will attempt reconnection automatically...");
            break;
            
        case WStype_CONNECTED:
            Serial.println("WebSocket Connected!");
            wsConnected = true;
            Serial.printf("Connected to: %s:%d%s\n", ws_server_url, ws_server_port, ws_path);
            // Send initial message
            webSocket.sendTXT("{\"type\":\"hello\",\"client\":\"ESP32\"}");
            break;
            
        case WStype_TEXT:
            Serial.printf("Received Text: %s\n", payload);
            break;
            
        case WStype_BIN:
            Serial.printf("Received binary: %u bytes\n", length);
            if (deviceConnected) {
                pCharacteristic->setValue(payload, length);
                pCharacteristic->notify();
            }
            break;
            
        case WStype_ERROR:
            Serial.println("WebSocket Error!");
            wsConnected = false;
            break;
            
        case WStype_PING:
            Serial.println("Ping received");
            break;
            
        case WStype_PONG:
            Serial.println("Pong received");
            break;
    }
}

// BLE Server Callbacks
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("BLE Client Connected");
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("BLE Client Disconnected");
    }
};

// Function to connect to WiFi
void connectToWiFi() {
    Serial.printf("Connecting to WiFi network: %s\n", ssid);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
}

// Add these variables at the top with other constants
const char* http_server_url = "http://192.168.1.254:5005";
bool http_test_passed = false;

// Add this function to test HTTP connectivity
bool testHTTPConnection() {
    HTTPClient http;
    
    Serial.println("Testing HTTP connection...");
    String test_url = String(http_server_url) + "/esp32-test";
    
    Serial.printf("Connecting to: %s\n", test_url.c_str());
    http.begin(test_url);
    
    int httpCode = http.GET();
    
    if (httpCode > 0) {
        Serial.printf("HTTP Response code: %d\n", httpCode);
        String payload = http.getString();
        Serial.printf("Response: %s\n", payload.c_str());
        
        http.end();
        return httpCode == 200;
    }
    else {
        Serial.printf("HTTP GET failed, error: %s\n", http.errorToString(httpCode).c_str());
        http.end();
        return false;
    }
}

// Modify the setup function
void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\nStarting ESP32...");

    // Connect to WiFi
    connectToWiFi();

    // Test HTTP connection first
    if (testHTTPConnection()) {
        Serial.println("HTTP test passed! Proceeding with WebSocket connection...");
        http_test_passed = true;
    } else {
        Serial.println("HTTP test failed! Check server address and port.");
        http_test_passed = false;
    }

    // Only proceed with WebSocket if HTTP test passed
    if (http_test_passed) {
        // Initialize WebSocket with more detailed configuration
        Serial.println("Initializing WebSocket connection...");
        webSocket.begin(ws_server_url, ws_server_port, ws_path);
        webSocket.onEvent(webSocketEvent);
        webSocket.setReconnectInterval(5000);
        webSocket.enableHeartbeat(15000, 3000, 2);
        
        // Set additional WebSocket options
        webSocket.setExtraHeaders("User-Agent: ESP32\r\nOrigin: ESP32Client");
        
        Serial.printf("Attempting connection to WebSocket server: %s:%d%s\n", 
                     ws_server_url, ws_server_port, ws_path);
    }

    // Initialize BLE
    initializeBLE();
}

// Add this function to initialize BLE (moved from setup)
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
    Serial.println("BLE service started, waiting for client connection...");
}

void loop() {
    // Only run WebSocket operations if HTTP test passed
    if (http_test_passed) {
        webSocket.loop();

        // Monitor WebSocket connection
        if (!wsConnected && (millis() - lastConnectionAttempt > connectionTimeout)) {
            // Try HTTP test again before attempting WebSocket reconnection
            if (testHTTPConnection()) {
                Serial.println("HTTP still accessible, attempting WebSocket reconnect...");
                Serial.printf("Connecting to: %s:%d%s\n", ws_server_url, ws_server_port, ws_path);
                webSocket.disconnect();
                webSocket.begin(ws_server_url, ws_server_port, ws_path);
                lastConnectionAttempt = millis();
            } else {
                Serial.println("HTTP test failed, server might be down");
                delay(5000);  // Wait longer before retry
            }
        }
    } else {
        // Periodically retry HTTP test if it failed
        static unsigned long lastHTTPTest = 0;
        if (millis() - lastHTTPTest > 10000) {  // Try every 10 seconds
            http_test_passed = testHTTPConnection();
            lastHTTPTest = millis();
        }
    }

    // Rest of your loop code...
    if (deviceConnected) {
        String value = pCharacteristic->getValue();
        if (value.length() > 0) {
            Serial.printf("Received from BLE client: %s\n", value.c_str());
            if (wsConnected) {
                webSocket.sendTXT(value.c_str());
            }
        }
    }

    delay(100);
}