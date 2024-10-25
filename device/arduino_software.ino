#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "BluetoothA2DPSink.h"

// Configuration
const char* ssid = "your_SSID";
const char* password = "your_PASSWORD";
const char* serverName = "http://your-flask-server/upload";

// Bluetooth A2DP for audio output
BluetoothA2DPSink a2dp_sink;

// Camera settings
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// LED Indicators
const int wifiStatusLED = 2;    // GPIO pin for Wi-Fi status
const int cameraStatusLED = 4;  // GPIO pin for Camera status
const int dataTransmissionLED = 16; // GPIO pin for Data Transmission status

// Initialize the camera
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
  
  if(psramFound()){
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    digitalWrite(cameraStatusLED, LOW);
    return false;
  }
  Serial.println("Camera initialized");
  digitalWrite(cameraStatusLED, HIGH);
  return true;
}

// Callback function for Bluetooth audio output
void audio_data_callback(const uint8_t* data, uint32_t len) {
  // Implement actual microphone capture and streaming logic here
}

void setup() {
  Serial.begin(115200);
  
  // Initialize LEDs
  pinMode(wifiStatusLED, OUTPUT);
  pinMode(cameraStatusLED, OUTPUT);
  pinMode(dataTransmissionLED, OUTPUT);
  
  digitalWrite(wifiStatusLED, LOW);
  digitalWrite(cameraStatusLED, LOW);
  digitalWrite(dataTransmissionLED, LOW);
  
  // Connect to Wi-Fi with timeout
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  unsigned long startAttemptTime = millis();
  const unsigned long wifiTimeout = 20000; // 20 seconds

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < wifiTimeout) {
    delay(1000);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi");
    digitalWrite(wifiStatusLED, HIGH);
  } else {
    Serial.println("\nFailed to connect to WiFi");
    // Optionally, implement retry logic or enter deep sleep
  }

  // Start camera
  if (!startCamera()) {
    Serial.println("Camera could not be initialized. Please check connections.");
    // Optionally, implement retry logic or enter deep sleep
  }

  // Set up Bluetooth audio sink (output)
  a2dp_sink.start("ESP32_A2DP_Sink");
  a2dp_sink.set_stream_reader(audio_data_callback);
}

void loop() {
  if(WiFi.status() == WL_CONNECTED){
    digitalWrite(dataTransmissionLED, HIGH);
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      digitalWrite(dataTransmissionLED, LOW);
      return;
    }

    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST(fb->buf, fb->len);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }

    esp_camera_fb_return(fb);
    http.end();
    digitalWrite(dataTransmissionLED, LOW);
  } else {
    Serial.println("WiFi not connected");
    digitalWrite(wifiStatusLED, LOW);
  }
  
  delay(5000); // Send image every 5 seconds
}