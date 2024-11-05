#include "driver/i2s.h"

// I2S Microphone pins
#define I2S_WS 25       // Word Select (LRC) pin
#define I2S_SD 22       // Serial Data (DOUT) pin
#define I2S_SCK 26      // Serial Clock (BCLK) pin

#define SAMPLE_RATE 16000
#define BLOCK_SIZE 1024

i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = BLOCK_SIZE,
    .use_apll = false
};

i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
};

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\nI2S Microphone Test");
    
    esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.printf("Failed installing driver: %d\n", err);
        while (1);
    }

    err = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (err != ESP_OK) {
        Serial.printf("Failed setting pin: %d\n", err);
        while (1);
    }

    Serial.println("I2S driver installed.");
}

void loop() {
    static uint32_t lastPrint = 0;
    static int32_t lastMaxValue = 0;
    
    int32_t samples[BLOCK_SIZE];
    size_t bytes_read = 0;
    
    esp_err_t err = i2s_read(I2S_NUM_0, samples, sizeof(samples), &bytes_read, portMAX_DELAY);
    
    if (err == ESP_OK) {
        int32_t max_value = 0;
        
        // Process samples to find max value
        for(int i = 0; i < BLOCK_SIZE/4; i++) {
            int32_t sample = samples[i] >> 14;  // Convert to 16-bit
            sample = abs(sample);               // Get absolute value
            if (sample > max_value) {
                max_value = sample;
            }
        }
        
        // Update the last max value
        if (max_value > lastMaxValue) {
            lastMaxValue = max_value;
        }
        
        // Print every 100ms if there's significant sound
        if (millis() - lastPrint >= 100) {
            if (lastMaxValue > 1000) {  // Adjust this threshold as needed
                Serial.print("Sound Level: ");
                Serial.print(lastMaxValue);
                Serial.print(" | ");
                
                // Print visual meter
                int bars = map(lastMaxValue, 0, 30000, 0, 40);
                for (int i = 0; i < 40; i++) {
                    if (i < bars) Serial.print("=");
                    else Serial.print(" ");
                }
                Serial.println("|");
            }
            
            lastPrint = millis();
            lastMaxValue = 0;  // Reset for next period
        }
    }
} 