#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// Basic configuration
const char* ssid = "17K2.4";
const char* password = "9852587137";
const char* serverName = "https://server.intelliroute-ai.com/upload";

// LED pin
const int LED_PIN = 33;

// Pin definitions for ESP32-CAM
#define CAM_PIN_PWDN    32
#define CAM_PIN_RESET   -1
#define CAM_PIN_XCLK    0
#define CAM_PIN_SIOD    26
#define CAM_PIN_SIOC    27
#define CAM_PIN_D7      35
#define CAM_PIN_D6      34
#define CAM_PIN_D5      39
#define CAM_PIN_D4      36
#define CAM_PIN_D3      21
#define CAM_PIN_D2      19
#define CAM_PIN_D1      18
#define CAM_PIN_D0      5
#define CAM_PIN_VSYNC   25
#define CAM_PIN_HREF    23
#define CAM_PIN_PCLK    22

void setup() {
    Serial.begin(115200);
    
    // Initialize camera with basic config
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;  // Using 2 frame buffers for better performance
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

    // Initialize camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.println("Camera init failed");
        return;
    }
    
    pinMode(LED_PIN, OUTPUT);
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi Connected");
    
    digitalWrite(LED_PIN, HIGH);
}

void loop() {
    // Take picture
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        delay(1000);
        return;
    }

    // Send to server
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverName);
        http.addHeader("Content-Type", "image/jpeg");
        
        digitalWrite(LED_PIN, LOW);
        int httpCode = http.POST(fb->buf, fb->len);
        digitalWrite(LED_PIN, HIGH);
        
        if (httpCode > 0) {
            Serial.printf("HTTP code: %d\n", httpCode);
        }
        http.end();
    }

    esp_camera_fb_return(fb);
    delay(5000);
}
