#include <WiFi.h>
#include <WebSockets_Generic.h>
#include <ArduinoJson.h>
#include <M5Atom.h>
#include <driver/i2s.h>

// WiFi credentials
const char* ssid = "17K2.4";
const char* password = "9852587137";

// WebSocket settings
const char* websocket_server = "server.intelliroute-ai.com";
const int websocket_port = 443;
const char* websocket_path = "/ws/audio";

// M5 Atom Echo I2S pins
#define CONFIG_I2S_BCK_PIN 19
#define CONFIG_I2S_LRCK_PIN 33
#define CONFIG_I2S_DATA_PIN 22
#define CONFIG_I2S_DATA_IN_PIN 23

#define SPEAKER_I2S_NUMBER I2S_NUM_0
#define MIC_I2S_NUMBER I2S_NUM_1

WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("### WebSocket Disconnected ###");
            break;
            
        case WStype_CONNECTED:
            Serial.println("### WebSocket Connected ###");
            Serial.printf("Connected to url: %s\n", payload);
            webSocket.sendTXT("Hello from M5 Atom Echo!");
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
    M5.begin(true, false, true);  // Initialize M5Atom with Serial enabled
    Serial.println("\n\n=== M5 Atom Echo WebSocket Client Starting ===");
    Serial.println("Initializing...");
    delay(1000);
    
    // Configure I2S for the PDM microphone
    i2s_config_t i2s_mic_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_PDM),
        .sample_rate = 44100,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 64,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t i2s_mic_pin_config = {
        .bck_io_num = I2S_PIN_NO_CHANGE,
        .ws_io_num = CONFIG_I2S_LRCK_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = CONFIG_I2S_DATA_IN_PIN
    };

    // Initialize I2S for microphone
    esp_err_t result = i2s_driver_install(MIC_I2S_NUMBER, &i2s_mic_config, 0, NULL);
    if (result != ESP_OK) {
        Serial.println("Error installing I2S mic driver!");
        while(1);
    }

    result = i2s_set_pin(MIC_I2S_NUMBER, &i2s_mic_pin_config);
    if (result != ESP_OK) {
        Serial.println("Error setting I2S mic pins!");
        while(1);
    }

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
        
        webSocket.beginSSL(websocket_server, websocket_port, websocket_path);
        webSocket.onEvent(webSocketEvent);
        webSocket.setReconnectInterval(5000);
        
        Serial.println("WebSocket initialization complete");
        Serial.println("Waiting for WebSocket connection...");
    }
}

void loop() {
    M5.update();
    
    if (WiFi.status() == WL_CONNECTED) {
        webSocket.loop();
        
        // Read and send audio data every 100ms
        static unsigned long lastSend = 0;
        if (millis() - lastSend > 100) {
            lastSend = millis();
            
            // Buffer for audio samples
            size_t bytes_read = 0;
            const int samplesCount = 1024;
            int16_t samples[samplesCount];
            
            // Read audio data from PDM microphone
            esp_err_t result = i2s_read(MIC_I2S_NUMBER, samples, sizeof(samples), &bytes_read, portMAX_DELAY);
            
            if (result == ESP_OK && bytes_read > 0) {
                // Convert 16-bit samples to 8-bit for transmission
                const int audioSize = bytes_read / 2;
                uint8_t audioData[audioSize];
                
                for (int i = 0; i < audioSize; i++) {
                    // Scale 16-bit to 8-bit
                    audioData[i] = (uint8_t)((samples[i] + 32768) / 256);
                }
                
                Serial.println("Sending audio data...");
                Serial.printf("Data size: %d bytes\n", audioSize);
                
                // Send the audio data
                webSocket.sendBIN(audioData, audioSize);
            }
        }
    } else {
        Serial.println("WiFi connection lost!");
        delay(1000);
    }
}