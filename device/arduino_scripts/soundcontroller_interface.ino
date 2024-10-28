#include <WiFi.h>
#include <WebSocketsClient.h>
#include "driver/i2s.h"

// Define your Wi-Fi credentials
const char* primary_ssid = "17k2.5";
const char* primary_password = "9852587137";

// Static IP Configuration
IPAddress local_IP(192, 168, 1, 200);   // Assign an unused IP in your network range
IPAddress gateway(192, 168, 1, 254);    // Your router's IP (default gateway)
IPAddress subnet(255, 255, 255, 0);     // Subnet mask
IPAddress primaryDNS(8, 8, 8, 8);       // Google's public DNS
IPAddress secondaryDNS(8, 8, 4, 4);     // Google's secondary DNS

// WebSocket server configuration
const char* serverHost = "server.intelliroute-ai.com";  // WebSocket host (no https://)
const uint16_t serverPort = 443;  // Secure WebSocket uses port 443
const char* serverPath = "/upload";  // WebSocket path

// WebSocket connection to the backend
WebSocketsClient webSocket;

// I2S setup (for audio input and output)
void setupI2S() {
  Serial.println("Setting up I2S...");

  i2s_config_t i2s_config = {
      .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX | I2S_MODE_RX),  // Master mode with TX (output) and RX (input)
      .sample_rate = 16000,  // Adjust the sample rate as needed
      .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,  // 16-bit audio
      .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,  // Stereo format
      .communication_format = I2S_COMM_FORMAT_I2S_MSB,
      .intr_alloc_flags = 0,  // Default interrupt allocation
      .dma_buf_count = 8,
      .dma_buf_len = 64,
      .use_apll = false
  };

  // I2S pin configuration
  i2s_pin_config_t pin_config = {
      .bck_io_num = 26,    // Bit Clock pin
      .ws_io_num = 25,     // Word Select pin (LRCK)
      .data_out_num = 21,  // Speaker Data Out (GPIO21)
      .data_in_num = 22    // Microphone Data In (GPIO22)
  };

  // Install and start I2S driver
  esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  if (err != ESP_OK) {
    Serial.printf("I2S driver installation failed: %d\n", err);
    return;
  }

  err = i2s_set_pin(I2S_NUM_0, &pin_config);
  if (err != ESP_OK) {
    Serial.printf("I2S pin setting failed: %d\n", err);
    return;
  }

  Serial.println("I2S setup complete.");
}

// Function to output audio to the speaker
void outputAudioToSpeaker(uint8_t* audioData, size_t length) {
  i2s_write(I2S_NUM_0, audioData, length, NULL, portMAX_DELAY);  // Send audio to the speaker
}

// WebSocket event handling
void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("WebSocket Disconnected");
      break;
    case WStype_CONNECTED:
      Serial.println("WebSocket Connected");
      // Optionally send a message when connected
      webSocket.sendTXT("ESP32 connected");
      break;
    case WStype_TEXT:
      Serial.printf("Received Text: %s\n", payload);
      break;
    case WStype_BIN:
      Serial.println("Binary data (audio) received from backend.");
      outputAudioToSpeaker(payload, length);
      break;
    case WStype_ERROR:
      Serial.println("WebSocket Error");
      break;
    default:
      break;
  }
}

// Wi-Fi setup
void setupWiFi() {
  Serial.print("Connecting to WiFi...");

  // Attempt to configure the ESP32 with a static IP
  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  }

  WiFi.begin(primary_ssid, primary_password);

  int retry_count = 0;
  while (WiFi.status() != WL_CONNECTED && retry_count < 20) {  // Add retry mechanism
    delay(500);
    Serial.print(".");
    retry_count++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi");
  } else {
    Serial.println("\nFailed to connect to WiFi");
    while (true);  // Stop further execution if Wi-Fi fails
  }
}

// WebSocket setup
void setupWebSocket() {
  Serial.println("Setting up WebSocket...");
  webSocket.beginSSL(serverHost, serverPort, serverPath);
  webSocket.onEvent(webSocketEvent);
  Serial.println("WebSocket setup complete.");
}

// Function to stream audio data to the backend
bool streamAudioToBackend(uint8_t* audioData, size_t& bytesRead) {
  esp_err_t err = i2s_read(I2S_NUM_0, (void*)audioData, 512, &bytesRead, portMAX_DELAY);
  if (err != ESP_OK) {
    Serial.printf("I2S read error: %d\n", err);
    return false;
  }
  if (bytesRead > 0) {
    webSocket.sendBIN(audioData, bytesRead);
    Serial.printf("Sent %d bytes of audio data.\n", bytesRead);
  }
  return true;
}

// Mock implementations of missing functions
bool detectWakeWord() {
  // Implement actual wake word detection logic here
  // For testing, trigger wake word detection every 10 seconds
  static unsigned long lastTime = 0;
  if (millis() - lastTime > 10000) {  // Every 10 seconds
    lastTime = millis();
    return true;
  }
  return false;
}

String listenForCommand() {
  // Implement actual command listening here
  // For testing, return "Let's chat" after wake word
  return "Let's chat";
}

void turnOnLight() {
  // Implement actual light control here
  Serial.println("Turning on the light...");
}

void setup() {
  Serial.begin(115200);
  setupI2S();
  setupWiFi();
  setupWebSocket();
}

void loop() {
  webSocket.loop();  // Keep WebSocket connection active

  static bool chatSession = false;

  if (!chatSession) {
    // Listen for wake word
    if (detectWakeWord()) {
      Serial.println("Wake word detected.");
      String command = listenForCommand();
      Serial.printf("Command: %s\n", command.c_str());
      if (command == "Let's chat") {
        chatSession = true;
        Serial.println("Starting chat session.");
      } else if (command == "Turn on the light") {
        turnOnLight();
      }
    }
  } else {
    // In chat session: stream audio to backend
    uint8_t audioData[512];
    size_t bytesRead = 0;
    if (streamAudioToBackend(audioData, bytesRead)) {
      // Successfully sent audio data
    } else {
      Serial.println("Failed to stream audio.");
      chatSession = false;  // Exit chat session on failure
    }

    // Exit chat session after sending 5 audio chunks
    static int audioChunksSent = 0;
    audioChunksSent++;
    if (audioChunksSent > 5) {
      Serial.println("Ending chat session.");
      chatSession = false;
      audioChunksSent = 0;
    }
  }

  delay(10);  // Small delay to prevent watchdog resets
}
