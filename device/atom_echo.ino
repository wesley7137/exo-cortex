#include <M5Atom.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <driver/i2s.h>
#include "BluetoothA2DPSink.h"

// Configuration
const char* ssid = "your_SSID";
const char* password = "your_PASSWORD";
const char* serverName = "http://your-flask-server/chat";  // Changed to chat endpoint

// Bluetooth A2DP for audio output
BluetoothA2DPSink a2dp_sink;

// I2S configuration for M5 Atom Echo's built-in PDM microphone
#define I2S_WS 19
#define I2S_SD 33
#define I2S_SCK 23
#define SAMPLE_RATE 16000
#define SAMPLE_BITS 16
#define CHANNELS 1
#define BUFFER_SIZE 512

// LED status indicator (M5 Atom has built-in LED matrix)
const int STATUS_LED = 27;

// I2S driver configuration
void configureI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = BUFFER_SIZE,
        .use_apll = false,
        .tx_desc_auto_clear = true,
        .fixed_mclk = 0
    };
    
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK,
        .ws_io_num = I2S_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_SD
    };
    
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
}

// Audio data callback
void audio_data_callback(const uint8_t* data, uint32_t len) {
    // Process audio data and send to server
    if(WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverName);
        http.addHeader("Content-Type", "audio/raw");
        
        int httpResponseCode = http.POST(data, len);
        
        if (httpResponseCode > 0) {
            String response = http.getString();
            // Process response from AI assistant
            Serial.println(response);
        }
        
        http.end();
    }
}

void setup() {
    M5.begin(true, false, true);  // Initialize M5Atom (param: serial, I2C, display)
    Serial.begin(115200);
    
    // Initialize LED matrix
    M5.dis.drawpix(0, 0xf00000);  // Red while connecting
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        M5.dis.drawpix(0, 0x00f000);  // Green when connected
        Serial.println("\nWiFi Connected");
    }
    
    // Configure I2S for microphone
    configureI2S();
    
    // Initialize Bluetooth audio output
    a2dp_sink.start("M5Atom_Assistant");
    a2dp_sink.set_stream_reader(audio_data_callback);
}

void loop() {
    M5.update();  // Update button state
    
    // Read audio data from I2S microphone
    size_t bytes_read = 0;
    uint8_t audio_buffer[BUFFER_SIZE];
    
    i2s_read(I2S_NUM_0, audio_buffer, BUFFER_SIZE, &bytes_read, portMAX_DELAY);
    
    if(bytes_read > 0) {
        // Process and send audio data
        audio_data_callback(audio_buffer, bytes_read);
    }
    
    // Visual feedback for data transmission
    M5.dis.drawpix(0, 0x0000f0);  // Blue during transmission
    delay(100);
    if(WiFi.status() == WL_CONNECTED) {
        M5.dis.drawpix(0, 0x00f000);  // Back to green
    }
    
    delay(10);  // Small delay to prevent overwhelming the system
}
