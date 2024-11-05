#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"
#include <ArduinoJson.h>
#include <esp_now.h>

// WiFi credentials
const char* ssid = "17K2.4";
const char* password = "9852587137";

// Server details
const char* serverUrl = "http://192.168.1.238:8000/upload";

// ESP-NOW MAC Address of audio ESP32 (you'll need to get this from the audio ESP32)
uint8_t audioESPAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}; // Replace with actual MAC

// Camera pins for AI Thinker ESP32-CAM
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

// LED Flash pin
#define FLASH_GPIO_NUM 4

// ESP-NOW message structure
typedef struct {
    char command[32];
} ESPNOWMessage;

// Callback when data is received via ESP-NOW
void OnDataRecv(const uint8_t *mac_addr, const uint8_t *data, int data_len) {
    ESPNOWMessage message;
    memcpy(&message, data, sizeof(message));
    
    if (strcmp(message.command, "capture") == 0) {
        captureAndSendImage();
    }
}

void setup() {
    Serial.begin(115200);
    
    // Print MAC Address
    Serial.print("ESP32-CAM MAC Address:  ");
    Serial.println(WiFi.macAddress());
    
    // Initialize flash LED as output
    pinMode(FLASH_GPIO_NUM, OUTPUT);
    digitalWrite(FLASH_GPIO_NUM, LOW);

    // Initialize camera
    if (!setupCamera()) {
        Serial.println("Camera setup failed!");
        return;
    }

    // Initialize WiFi in Station mode
    WiFi.mode(WIFI_AP_STA);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");

    // Initialize ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    // Register callback for incoming ESP-NOW messages
    esp_now_register_recv_cb(OnDataRecv);
}

bool setupCamera() {
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

    // Initialize with high specs to pre-allocate larger buffers
    if (psramFound()) {
        config.frame_size = FRAMESIZE_UXGA;
        config.jpeg_quality = 10;  // 0-63, lower means higher quality
        config.fb_count = 2;
    } else {
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
    }

    // Initialize the camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return false;
    }

    sensor_t * s = esp_camera_sensor_get();
    s->set_framesize(s, FRAMESIZE_VGA);  // Set lower resolution for faster uploads
    
    return true;
}

bool captureAndSendImage() {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        return false;
    }

    // Flash the LED
    digitalWrite(FLASH_GPIO_NUM, HIGH);
    delay(100);
    digitalWrite(FLASH_GPIO_NUM, LOW);

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");
    
    // Send the image data
    int httpResponseCode = http.POST(fb->buf, fb->len);
    
    // Free the camera buffer
    esp_camera_fb_return(fb);

    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println("Image uploaded successfully");
        Serial.println("Server response: " + response);
        http.end();
        return true;
    } else {
        Serial.printf("Image upload failed, error: %s\n", http.errorToString(httpResponseCode).c_str());
        http.end();
        return false;
    }
}

void loop() {
    // The device now waits for ESP-NOW messages
    // No need to check Serial for commands anymore
    delay(10);
}