#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "17K2.4";
const char* password = "9852587137";

// WebSocket settings
const char* websocket_server = "your_flask_server_ip";
const int websocket_port = 5000;  // Match your Flask server port
const char* websocket_path = "/socket.io/?EIO=4&transport=websocket";

WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("### WebSocket Disconnected ###");
            break;
            
        case WStype_CONNECTED:
            Serial.println("### WebSocket Connected ###");
            Serial.printf("Connected to url: %s\n", payload);
            // Send a test message
            webSocket.sendTXT("Hello from ESP32!");
            break;
            
        case WStype_TEXT:
            Serial.println("### Received WebSocket Message ###");
            Serial.printf("Message: %s\n", payload);
            break;
            
        case WStype_BIN:
            Serial.println("### Received Binary Message ###");
            Serial.printf("Length: %u\n", length);
            break;
            
        case WStype_ERROR:
            Serial.println("### WebSocket Error ###");
            break;
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("\n\n=== ESP32 WebSocket Client Starting ===");
    Serial.println("Initializing...");
    delay(1000);
    
    // WiFi Connection
    Serial.printf("Attempting to connect to WiFi network: %s\n", ssid);
    WiFi.begin(ssid, password);
    
    int timeout = 0;
    Serial.println("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED && timeout < 30) {
        delay(1000);
        Serial.printf("Connection attempt %d of 30...\n", timeout + 1);
        timeout++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n=== WiFi Connection Successful! ===");
        Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());

        // WebSocket Connection
        Serial.println("\n=== Initializing WebSocket Connection ===");
        Serial.printf("Server: %s\n", websocket_server);
        Serial.printf("Port: %d\n", websocket_port);
        Serial.printf("Path: %s\n", websocket_path);
        
        // Changed to beginSSL for secure connection
        webSocket.beginSSL(websocket_server, websocket_port, websocket_path);
        webSocket.onEvent(webSocketEvent);
        webSocket.setReconnectInterval(5000);
        
        Serial.println("WebSocket initialization complete");
        Serial.println("Waiting for WebSocket connection...");
    }
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        webSocket.loop();
        
        // For testing, send some dummy audio data every 5 seconds
        static unsigned long lastSend = 0;
        if (millis() - lastSend > 5000) {
            lastSend = millis();
            
            // Create dummy audio data with a simple pattern
            const int audioSize = 32;
            uint8_t dummyAudio[audioSize];
            
            // Fill with a simple sine-wave pattern for testing
            for(int i = 0; i < audioSize; i++) {
                dummyAudio[i] = (uint8_t)(127 + 127 * sin(i * 2 * PI / audioSize));
            }
            
            Serial.println("Sending dummy audio data...");
            Serial.printf("Data size: %d bytes\n", audioSize);
            
            // Send the binary data with a header byte
            webSocket.sendBIN(dummyAudio, audioSize);
        }
    } else {
        Serial.println("WiFi connection lost!");
        delay(1000);
    }
}
