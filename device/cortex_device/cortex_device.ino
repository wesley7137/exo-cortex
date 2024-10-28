unsigned long previousMillis = 0;
unsigned long interval = 30000;

#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "BluetoothA2DPSource.h"
#include "driver/i2s.h"


// Camera pin definitions
#if !defined(CAMERA_MODEL_AI_THINKER)
  #define CAMERA_MODEL_AI_THINKER
  #define PWDN_GPIO_NUM     32
  #define RESET_GPIO_NUM    -1
  #define XCLK_GPIO_NUM      0
  #define SIOD_GPIO_NUM     26
  #define SIOC_GPIO_NUM     27
  #define Y9_GPIO_NUM       35
  #define Y8_GPIO_NUM       34
  #define Y7_GPIO_NUM       39
  #define Y6_GPIO_NUM       36
  #define Y5_GPIO_NUM       21
  #define Y4_GPIO_NUM       19
  #define Y3_GPIO_NUM       18
  #define Y2_GPIO_NUM        5
  #define VSYNC_GPIO_NUM    25
  #define HREF_GPIO_NUM     23
  #define PCLK_GPIO_NUM     22
#endif

// Configuration
const char* ssid = "17K2.4";
const char* password = "9852587137";
const char* serverName = "https://server.intelliroute-ai.com/upload";

// Audio Configuration
BluetoothA2DPSource a2dp_source;
const int BUFFER_SIZE = 512;
int16_t audio_buffer[BUFFER_SIZE];

// I2S Configuration
#define I2S_WS_PIN 12
#define I2S_SD_PIN 2
#define I2S_SCK_PIN 4
#define I2S_PORT I2S_NUM_0
#define I2S_SAMPLE_RATE 44100
#define I2S_CHANNELS 2

// LED Indicators
const int wifiStatusLED = 4;
const int cameraStatusLED = 33;
const int dataTransmissionLED = 13;

void WiFiStationDisconnected(WiFiEvent_t event, WiFiEventInfo_t info){
    Serial.println("Disconnected from WiFi access point");
    Serial.print("WiFi lost connection. Reason: ");
    Serial.println(info.wifi_sta_disconnected.reason);
    Serial.println("Trying to Reconnect");
    digitalWrite(wifiStatusLED, LOW);
}

void reconnectWiFi() {
    if (WiFi.status() != WL_CONNECTED) {
        WiFi.disconnect();
        delay(1000);
        WiFi.begin(ssid, password);
        
        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 20) {
            delay(500);
            Serial.print(".");
            attempts++;
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\nReconnected to WiFi");
            digitalWrite(wifiStatusLED, HIGH);
        }
    }
}

void i2s_init() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = I2S_SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = BUFFER_SIZE,
        .use_apll = false,
        .tx_desc_auto_clear = true,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_SD_PIN
    };

    esp_err_t err = i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.printf("Failed installing I2S driver: %d\n", err);
        return;
    }

    err = i2s_set_pin(I2S_PORT, &pin_config);
    if (err != ESP_OK) {
        Serial.printf("Failed setting I2S pins: %d\n", err);
        return;
    }

    i2s_start(I2S_PORT);
}

int32_t get_sound_data(Frame* frames, int32_t len) {
    size_t bytes_read = 0;
    i2s_read(I2S_PORT, audio_buffer, len * sizeof(Frame), &bytes_read, portMAX_DELAY);
    
    for (int i = 0; i < len; i++) {
        frames[i].channel1 = audio_buffer[i*2];
        frames[i].channel2 = audio_buffer[i*2 + 1];
    }
    
    return len;
}

bool startCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.jpeg_quality = 12;
    config.fb_count = 1;

    if(psramFound()){
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 10;
        config.fb_count = 2;
    } else {
        config.frame_size = FRAMESIZE_VGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
    }

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x\n", err);
        return false;
    }

    sensor_t * s = esp_camera_sensor_get();
    s->set_brightness(s, 0);     // -2 to 2
    s->set_contrast(s, 0);       // -2 to 2
    s->set_saturation(s, 0);     // -2 to 2
    s->set_special_effect(s, 0); // 0 to 6 (0 - No Effect, 1 - Negative, 2 - Grayscale, 3 - Red Tint, 4 - Green Tint, 5 - Blue Tint, 6 - Sepia)
    s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
    s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
    s->set_wb_mode(s, 0);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
    s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
    s->set_aec2(s, 0);          // 0 = disable , 1 = enable
    s->set_gain_ctrl(s, 1);      // 0 = disable , 1 = enable
    s->set_agc_gain(s, 0);       // 0 to 30
    s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
    s->set_bpc(s, 0);           // 0 = disable , 1 = enable
    s->set_wpc(s, 1);           // 0 = disable , 1 = enable
    s->set_raw_gma(s, 1);       // 0 = disable , 1 = enable
    s->set_lenc(s, 1);          // 0 = disable , 1 = enable
    s->set_hmirror(s, 0);       // 0 = disable , 1 = enable
    s->set_vflip(s, 0);         // 0 = disable , 1 = enable
    s->set_dcw(s, 1);           // 0 = disable , 1 = enable
    s->set_colorbar(s, 0);      // 0 = disable , 1 = enable
    
    return true;
}


void setup() {
    Serial.begin(115200);
    
    if(!psramFound()) {
        Serial.println("Warning: PSRAM not found");
    }
    
    pinMode(wifiStatusLED, OUTPUT);
    pinMode(cameraStatusLED, OUTPUT);
    pinMode(dataTransmissionLED, OUTPUT);
    
    digitalWrite(wifiStatusLED, LOW);
    digitalWrite(cameraStatusLED, LOW);
    digitalWrite(dataTransmissionLED, LOW);
    
    i2s_init();
    
    WiFi.onEvent(WiFiStationDisconnected, WiFiEvent_t::ARDUINO_EVENT_WIFI_STA_DISCONNECTED);
    
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    unsigned long startAttemptTime = millis();
    const unsigned long wifiTimeout = 20000;

    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < wifiTimeout) {
        delay(500);
        Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nConnected to WiFi");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
        digitalWrite(wifiStatusLED, HIGH);
    } else {
        Serial.println("\nFailed to connect to WiFi");
        return;
    }

    if (!startCamera()) {
        Serial.println("Camera initialization failed");
        return;
    }

    a2dp_source.start("ESP32_Audio", get_sound_data);
    Serial.println("A2DP Source started");
}

void loop() {
    unsigned long currentMillis = millis();
    
    if ((WiFi.status() != WL_CONNECTED) && (currentMillis - previousMillis >= interval)) {
        Serial.println("WiFi connection lost. Attempting to reconnect...");
        reconnectWiFi();
        previousMillis = currentMillis;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        digitalWrite(dataTransmissionLED, HIGH);
        
        camera_fb_t * fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Camera capture failed");
            digitalWrite(dataTransmissionLED, LOW);
            delay(1000);
            return;
        }

        HTTPClient http;
        http.begin(serverName);
        http.addHeader("Content-Type", "image/jpeg");
        
        int httpResponseCode = http.POST(fb->buf, fb->len);
        
        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.printf("HTTP Response code: %d\n", httpResponseCode);
        } else {
            Serial.printf("Error sending POST: %d\n", httpResponseCode);
        }

        esp_camera_fb_return(fb);
        http.end();
        
        digitalWrite(dataTransmissionLED, LOW);
    }
    
    delay(20);
}
