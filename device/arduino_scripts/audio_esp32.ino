#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <esp_now.h>
#include "driver/i2s.h"
#include "FS.h"
#include "SD_MMC.h"

// WiFi credentials
const char* ssid = "17K2.4";
const char* password = "9852587137";

// ESP-NOW MAC Address of ESP32-CAM
uint8_t cameraESPAddress[] = {0x3C, 0x61, 0x05, 0x12, 0xA4, 0xBC};

WebSocketsClient webSocket;
bool complexTaskMode = false;
bool isRecording = false;
unsigned long recordingStartTime = 0;

// ESP-NOW message structure
typedef struct {
    char command[32];
} ESPNOWMessage;

// Callback when data is sent via ESP-NOW
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("Last Packet Send Status: ");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

// I2S Microphone pins
#define I2S_WS 25       // Word Select (LRC) pin
#define I2S_SD 22       // Serial Data (DOUT) pin
#define I2S_SCK 26      // Serial Clock (BCLK) pin

// I2S configuration
#define SAMPLE_RATE 16000
#define SAMPLE_BITS 16
#define CHANNELS 1
#define BLOCK_SIZE 1024

// I2S driver configuration
i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = BLOCK_SIZE,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
};

// I2S pin configuration
i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
};

// WAV header structure
struct WAVHeader {
    // RIFF chunk
    char riff_header[4] = {'R', 'I', 'F', 'F'};
    uint32_t wav_size;
    char wave_header[4] = {'W', 'A', 'V', 'E'};
    
    // fmt chunk
    char fmt_header[4] = {'f', 'm', 't', ' '};
    uint32_t fmt_chunk_size = 16;
    uint16_t audio_format = 1;
    uint16_t num_channels = CHANNELS;
    uint32_t sample_rate = SAMPLE_RATE;
    uint32_t byte_rate = SAMPLE_RATE * CHANNELS * (SAMPLE_BITS / 8);
    uint16_t sample_alignment = CHANNELS * (SAMPLE_BITS / 8);
    uint16_t bit_depth = SAMPLE_BITS;
    
    // data chunk
    char data_header[4] = {'d', 'a', 't', 'a'};
    uint32_t data_bytes;
};

// Buffer for recording
const int RECORDING_SECONDS = 5;
const int BUFFER_SIZE = SAMPLE_RATE * RECORDING_SECONDS * (SAMPLE_BITS / 8) * CHANNELS;
int16_t* recording_buffer = nullptr;
size_t buffer_index = 0;

// Function to start recording
void startRecording() {
    if (recording_buffer == nullptr) {
        recording_buffer = (int16_t*)malloc(BUFFER_SIZE);
    }
    if (recording_buffer == nullptr) {
        Serial.println("Failed to allocate recording buffer!");
        return;
    }
    buffer_index = 0;
    isRecording = true;
    recordingStartTime = millis();
    Serial.println("Recording started...");
}

// Function to save recording as WAV
void saveRecording() {
    if (!recording_buffer || buffer_index == 0) {
        Serial.println("No recording data to save!");
        return;
    }

    // Create WAV header
    WAVHeader header;
    header.data_bytes = buffer_index * sizeof(int16_t);
    header.wav_size = header.data_bytes + sizeof(WAVHeader) - 8;

    // Create filename with timestamp
    char filename[32];
    snprintf(filename, sizeof(filename), "/recording_%lu.wav", millis());
    
    // Open file for writing
    File file = SD_MMC.open(filename, FILE_WRITE);
    if (!file) {
        Serial.println("Failed to open file for writing!");
        return;
    }

    // Write header and data
    file.write((const uint8_t*)&header, sizeof(WAVHeader));
    file.write((const uint8_t*)recording_buffer, buffer_index * sizeof(int16_t));
    file.close();

    Serial.printf("Recording saved to %s\n", filename);
    
    // Free buffer
    free(recording_buffer);
    recording_buffer = nullptr;
    buffer_index = 0;
    isRecording = false;
}

void setup() {
    Serial.begin(115200);

    // Initialize WiFi in Station mode
    WiFi.mode(WIFI_AP_STA);
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());

    // Initialize ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    // Register peer (ESP32-CAM)
    esp_now_peer_info_t peerInfo;
    memcpy(peerInfo.peer_addr, cameraESPAddress, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("Failed to add peer");
        return;
    }

    // Register callback for ESP-NOW send operations
    esp_now_register_send_cb(OnDataSent);

    // Setup WebSocket for complex tasks
    webSocket.begin("192.168.1.238", 8005, "/ws/audio");  // Your actual IP address
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);

    Serial.println("\nReady for commands!");
    Serial.println("Available commands:");
    Serial.println("1: Take picture");
    Serial.println("2: Let's chat");
    Serial.println("3: Stop chat");
    Serial.println("4: Take note");

    // Initialize I2S
    esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.printf("Failed installing I2S driver: %d\n", err);
        return;
    }

    err = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (err != ESP_OK) {
        Serial.printf("Failed setting I2S pins: %d\n", err);
        return;
    }

    // The SPH0645 has a DC offset, so let's set up a filter
    i2s_set_clk(I2S_NUM_0, SAMPLE_RATE, I2S_BITS_PER_SAMPLE_32BIT, I2S_CHANNEL_MONO);
}

void handleLocalCommand(const char* command) {
    if (strcmp(command, "take picture") == 0) {
        // Send ESP-NOW message to ESP32-CAM
        ESPNOWMessage message;
        strcpy(message.command, "capture");
        
        esp_err_t result = esp_now_send(cameraESPAddress, (uint8_t *)&message, sizeof(message));
        if (result == ESP_OK) {
            Serial.println("Sent capture command to camera");
        } else {
            Serial.println("Error sending capture command");
        }
    }
    else if (strcmp(command, "lets chat") == 0) {
        Serial.println("Initiating complex task mode");
        // Create JSON message for server
        StaticJsonDocument<200> doc;
        doc["type"] = "command";
        doc["command"] = "lets_chat";
        
        String jsonString;
        serializeJson(doc, jsonString);
        
        // Send command to server
        webSocket.sendTXT(jsonString);
        complexTaskMode = true;
    }
    else if (strcmp(command, "stop chat") == 0) {
        Serial.println("Ending complex task mode");
        // Create JSON message for server
        StaticJsonDocument<200> doc;
        doc["type"] = "command";
        doc["command"] = "stop_chat";
        
        String jsonString;
        serializeJson(doc, jsonString);
        
        // Send command to server
        webSocket.sendTXT(jsonString);
        complexTaskMode = false;
    }
    else if (strcmp(command, "take note") == 0) {
        Serial.println("Starting note taking mode");
        // Create JSON message for server
        StaticJsonDocument<200> doc;
        doc["type"] = "command";
        doc["command"] = "take_note";
        
        String jsonString;
        serializeJson(doc, jsonString);
        
        // Send command to server
        webSocket.sendTXT(jsonString);
    }
    else if (strcmp(command, "record") == 0) {
        if (!isRecording) {
            Serial.println("Starting 5-second recording");
            // Create JSON message for server
            StaticJsonDocument<200> doc;
            doc["type"] = "command";
            doc["command"] = "start_recording";
            
            String jsonString;
            serializeJson(doc, jsonString);
            
            // Send command to server
            webSocket.sendTXT(jsonString);
            complexTaskMode = true;  // Enable microphone reading
        } else {
            Serial.println("Already recording!");
        }
    }
}

void handleWebSocketText(uint8_t * payload, size_t length) {
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, payload);
    
    if (!error) {
        const char* status = doc["status"];
        const char* message = doc["message"];
        
        if (strcmp(status, "success") == 0) {
            if (doc["type"] == "image_uploaded") {
                Serial.println("Image was uploaded successfully");
            }
            else if (strcmp(message, "Complex task mode activated") == 0) {
                complexTaskMode = true;
                Serial.println("Complex task mode activated by server");
            }
            else if (strcmp(message, "Complex task mode deactivated") == 0) {
                complexTaskMode = false;
                Serial.println("Complex task mode deactivated by server");
            }
            else if (strcmp(message, "Recording started") == 0) {
                isRecording = true;
                recordingStartTime = millis();
                Serial.println("Recording started - collecting 5 seconds of audio...");
            }
            else if (strcmp(message, "Recording saved") == 0) {
                isRecording = false;
                complexTaskMode = false;
                Serial.println("Recording completed and saved!");
                Serial.printf("Saved as: %s\n", doc["filename"].as<const char*>());
            }
        }
    }
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_CONNECTED:
            Serial.println("WebSocket Connected");
            break;
            
        case WStype_DISCONNECTED:
            Serial.println("WebSocket Disconnected");
            complexTaskMode = false;
            webSocket.begin("192.168.1.238", 8005, "/ws/audio");  // Attempt reconnect
            break;
            
        case WStype_TEXT:
            handleWebSocketText(payload, length);
            break;
            
        case WStype_BIN:
            // Don't print for every binary message to reduce serial noise
            break;
            
        case WStype_ERROR:
            Serial.println("WebSocket Error - Resetting connection");
            complexTaskMode = false;
            webSocket.begin("192.168.1.238", 8005, "/ws/audio");
            break;
    }
}

void readMicrophone() {
    int32_t samples[BLOCK_SIZE];
    size_t bytes_read = 0;
    
    esp_err_t err = i2s_read(I2S_NUM_0, samples, sizeof(samples), &bytes_read, portMAX_DELAY);
    
    if (err != ESP_OK) {
        Serial.printf("Failed reading I2S: %d\n", err);
        return;
    }

    if (complexTaskMode) {
        // Process samples using the same method as test_mic.ino
        int16_t processed_samples[BLOCK_SIZE/4];
        int32_t max_level = 0;
        
        // Process samples exactly like in test_mic.ino
        for(int i = 0; i < BLOCK_SIZE/4; i++) {
            int32_t sample = samples[i] >> 14;  // Convert to 16-bit
            processed_samples[i] = sample;       // Store the non-absolute value for transmission
            
            // Track max level using absolute value (for monitoring only)
            sample = abs(sample);
            if (sample > max_level) {
                max_level = sample;
            }
        }
        
        // Send to server
        bool success = webSocket.sendBIN((uint8_t*)processed_samples, BLOCK_SIZE/2);
        if (!success) {
            Serial.println("Failed to send audio data!");
        }

        // Print audio level occasionally (using same threshold as test_mic)
        static unsigned long lastPrint = 0;
        if (millis() - lastPrint > 1000) {
            if (max_level > 1000) {  // Same threshold as test_mic
                Serial.print("Sending audio - Level: ");
                Serial.print(max_level);
                Serial.print(" | ");
                
                // Print visual meter like test_mic
                int bars = map(max_level, 0, 30000, 0, 40);
                for (int i = 0; i < 40; i++) {
                    if (i < bars) Serial.print("=");
                    else Serial.print(" ");
                }
                Serial.println("|");
            }
            lastPrint = millis();
        }
    }
}

void loop() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');  // Read until newline
        command.trim();  // Remove any whitespace
        command.toLowerCase();  // Convert to lowercase for easier comparison
        
        if (command == "picture" || command == "take picture") {
            handleLocalCommand("take picture");
        }
        else if (command == "chat" || command == "lets chat") {
            handleLocalCommand("lets chat");
        }
        else if (command == "stop" || command == "stop chat") {
            handleLocalCommand("stop chat");
        }
        else if (command == "note" || command == "take note") {
            handleLocalCommand("take note");
        }
        else if (command == "record" || command == "start recording") {
            handleLocalCommand("record");
        }
        else {
            Serial.println("Unknown command. Available commands:");
            Serial.println("- picture (or take picture)");
            Serial.println("- chat (or lets chat)");
            Serial.println("- stop (or stop chat)");
            Serial.println("- note (or take note)");
            Serial.println("- record (or start recording)");
        }
    }
    
    if (complexTaskMode) {
        webSocket.loop();
        readMicrophone();
    }
    
    delay(10);
} 