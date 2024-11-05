#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <esp_now.h>
#include "driver/i2s.h"
#include "FS.h"
#include "SD_MMC.h"
#include "esp_mn_speech_commands.h"
#include "esp_process_sdkconfig.h"
#include "esp_mn_models.h"
#include "esp_wn_iface.h"
#include "esp_wn_models.h"
#include "esp_afe_sr_iface.h"
#include "esp_afe_sr_models.h"

// Add PSRAM configuration
#if CONFIG_IDF_TARGET_ESP32S3
#define BOARD_HAS_PSRAM
#endif

// ---------------------------
// WiFi Configuration
// ---------------------------
const char* ssid = "17K2.4";
const char* password = "9852587137";

// ---------------------------
// ESP-NOW Configuration
// ---------------------------
// MAC Address of ESP32-CAM
uint8_t cameraESPAddress[] = {0x3C, 0x61, 0x05, 0x12, 0xA4, 0xBC};

// ESP-NOW message structure
typedef struct {
    char command[32];
} ESPNOWMessage;

// ---------------------------
// WebSocket Configuration
// ---------------------------
WebSocketsClient webSocket;

// ---------------------------
// I2S Configuration
// ---------------------------
#define I2S_WS_PIN 42  // Word Select (LRC) pin for MSM261D3526H1CPM
#define I2S_SD_PIN 41  // Serial Data (DOUT) pin for MSM261D3526H1CPM
#define I2S_SCK_PIN -1  // Serial Clock (BCLK) pin not used for PDM microphone

// I2S settings
#define SAMPLE_RATE 16000
#define SAMPLE_BITS I2S_BITS_PER_SAMPLE_16BIT
#define CHANNELS 1
#define BLOCK_SIZE 1024

i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_PDM),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = SAMPLE_BITS,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = BLOCK_SIZE,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0,
    .mclk_multiple = I2S_MCLK_MULTIPLE_256,
    .bits_per_chan = I2S_BITS_PER_SAMPLE_16BIT
};

i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK_PIN,
    .ws_io_num = I2S_WS_PIN,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD_PIN
};

// ---------------------------
// SD Card Configuration
// ---------------------------
#define SD_CS_PIN    -1  // Not used for SD_MMC
#define SD_MMC_CARD   // Using SD_MMC instead of SPI

// ---------------------------
// WAV Header Structure
// ---------------------------
struct WAVHeader {
    char riff_header[4] = {'R', 'I', 'F', 'F'};
    uint32_t wav_size;
    char wave_header[4] = {'W', 'A', 'V', 'E'};
    char fmt_header[4] = {'f', 'm', 't', ' '};
    uint32_t fmt_chunk_size = 16;
    uint16_t audio_format = 1;
    uint16_t num_channels = CHANNELS;
    uint32_t sample_rate = SAMPLE_RATE;
    uint32_t byte_rate = SAMPLE_RATE * CHANNELS * (SAMPLE_BITS / 8);
    uint16_t sample_alignment = CHANNELS * (SAMPLE_BITS / 8);
    uint16_t bit_depth = SAMPLE_BITS;
    char data_header[4] = {'d', 'a', 't', 'a'};
    uint32_t data_bytes;
};

// ---------------------------
// Recording Configuration
// ---------------------------
const int RECORDING_SECONDS = 5;
const int BUFFER_SIZE = SAMPLE_RATE * RECORDING_SECONDS * (SAMPLE_BITS / 8) * CHANNELS;
int16_t* recording_buffer = nullptr;
size_t buffer_index = 0;

// ---------------------------
// Flags and Timers
// ---------------------------
bool complexTaskMode = false;
bool isRecording = false;
unsigned long recordingStartTime = 0;

// ---------------------------
// Wake Word Detection Configuration
// ---------------------------
const int WAKE_THRESHOLD = 1000;  // Adjust based on microphone sensitivity

// Add these constants for wake word detection
const int WAKE_WORD_DURATION = 1000;  // Duration to check for wake word in ms
const int WAKE_WORD_THRESHOLD = 3000;  // Adjust based on testing
bool wakeWordDetected = false;

// Speech recognition configurations
#define WAKE_WORD_DURATION 1000
#define COMMAND_TIMEOUT 5000
#define MAX_COMMAND_NUM 100

// Update the speech recognition variables
const esp_afe_sr_iface_t *afe_handle = &esp_afe_sr_v1;
esp_afe_sr_data_t *afe_data = NULL;
int detect_flag = 0;
afe_fetch_result_t *fetch_result = NULL;

// Add these defines for detection states
#define SR_WAKEUP_OK 2  // Wake word detected
#define SR_COMMAND_OK 3 // Command detected

// Command recognition state
bool speech_recognition_active = false;
unsigned long last_command_time = 0;


// ---------------------------
// Function Declarations
// ---------------------------
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status);
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length);
void handleWebSocketText(uint8_t * payload, size_t length);
void handleLocalCommand(const char* command);
void readMicrophone();
void startRecording();
void saveRecording();
void initializeESPNow();
void initializeWebSocket();
void initializeI2S();
void initializeSDCard();
bool detectWakeWord(int16_t sample);
void processCommand();
void initializeSpeechRecognition();
void handleCommand(int command_id);
void enterLowPowerMode();
void checkBatteryStatus();

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("Starting XIAO ESP32S3 Sense...");

    // Check PSRAM
    if (psramInit()) {
        Serial.println("PSRAM initialized successfully");
        // Allocate recording buffer in PSRAM if available
        recording_buffer = (int16_t*)ps_malloc(BUFFER_SIZE);
    } else {
        Serial.println("PSRAM initialization failed, using regular memory");
        recording_buffer = (int16_t*)malloc(BUFFER_SIZE);
    }

    if (recording_buffer == nullptr) {
        Serial.println("Failed to allocate recording buffer!");
        return;
    }
    Serial.println("Recording buffer allocated successfully");

    // Initialize WiFi
    Serial.println("Initializing WiFi...");
    WiFi.mode(WIFI_AP_STA);
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Initialize ESP-NOW
    initializeESPNow();

    // Initialize WebSocket
    initializeWebSocket();

    // Initialize I2S
    initializeI2S();

    // Initialize speech recognition
    initializeSpeechRecognition();

    Serial.println("Setup complete!");
}

void loop() {
    // Handle WebSocket
    webSocket.loop();

    // Check WebSocket connection
    checkWebSocketConnection();

    // Read microphone data
    readMicrophone();

    // Handle recording timeout
    if (isRecording && (millis() - recordingStartTime >= RECORDING_SECONDS * 1000)) {
        saveRecording();
    }

    // Add other tasks or command handling here
}

// ---------------------------
// Function Implementations
// ---------------------------

// ESP-NOW Send Callback
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("ESP-NOW Send Status: ");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Success" : "Fail");
}

// Initialize ESP-NOW
void initializeESPNow() {
    Serial.println("Initializing ESP-NOW...");
    WiFi.mode(WIFI_AP_STA); // Make sure this is set before esp_now_init()
    
    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    // Register peer with updated configuration
    esp_now_peer_info_t peerInfo = {};  // Initialize all fields to 0
    memcpy(peerInfo.peer_addr, cameraESPAddress, 6);
    peerInfo.channel = 0;  
    peerInfo.encrypt = false;
    peerInfo.ifidx = WIFI_IF_STA;  // Add this line to specify interface

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("Failed to add ESP-NOW peer");
        return;
    }

    esp_now_register_send_cb(OnDataSent);
    Serial.println("ESP-NOW initialized and peer added.");
}

// WebSocket Event Handler
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("⚠️ WebSocket Disconnected!");
            break;
            
        case WStype_CONNECTED:
            Serial.println("✅ WebSocket Connected!");
            break;
            
        case WStype_TEXT:
            Serial.print("📥 Received Text: ");
            Serial.println((char*)payload);
            handleWebSocketText(payload, length);
            break;
            
        case WStype_BIN:
            Serial.printf("📦 Received binary: %u bytes\n", length);
            break;
            
        case WStype_ERROR:
            Serial.println("❌ WebSocket Error!");
            break;
            
        case WStype_FRAGMENT_TEXT_START:
        case WStype_FRAGMENT_BIN_START:
            Serial.println("🔄 Fragment Start");
            break;
            
        case WStype_FRAGMENT:
            Serial.println("🔄 Fragment");
            break;
            
        case WStype_FRAGMENT_FIN:
            Serial.println("🔄 Fragment Finish");
            break;
    }
}

// Initialize WebSocket
void initializeWebSocket() {
    Serial.println("Initializing WebSocket...");
    // Change this IP to match your computer's IP address
    const char* serverIP = "192.168.1.238";  // Update this!
    webSocket.begin(serverIP, 8005, "/ws/audio");
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);
    Serial.println("WebSocket initialized.");
}

// Handle WebSocket Text Messages
void handleWebSocketText(uint8_t * payload, size_t length) {
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    
    if (error) {
        Serial.println("JSON parsing failed");
        return;
    }

    const char* command = doc["command"];
    if (command) {
        if (strcmp(command, "lets_chat") == 0) {
            complexTaskMode = true;
            Serial.println("Entering complex task mode");
        } else if (strcmp(command, "stop_chat") == 0) {
            complexTaskMode = false;
            wakeWordDetected = false;
            Serial.println("Exiting complex task mode");
        }
    }
}

// Handle Local Commands
void handleLocalCommand(const char* command) {
    // Implement command handling logic
    if (strcmp(command, "start_recording") == 0) {
        startRecording();
    } else if (strcmp(command, "stop_recording") == 0) {
        saveRecording();
    }
    // Add more commands as needed
}

// Initialize I2S
void initializeI2S() {
    Serial.println("Initializing I2S for MSM261D3526H1CPM microphone...");
    
    // Delete existing driver if any
    i2s_driver_uninstall(I2S_NUM_0);
    
    // Install and configure I2S driver
    esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.printf("Failed to install I2S driver: %d\n", err);
        return;
    }

    // Configure I2S pins
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_SD_PIN
    };

    err = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (err != ESP_OK) {
        Serial.printf("Failed to set I2S pins: %d\n", err);
        return;
    }

    // Set PDM mode
    err = i2s_set_pdm_rx_down_sample(I2S_NUM_0, I2S_PDM_DSR_8S);
    if (err != ESP_OK) {
        Serial.printf("Failed to set PDM mode: %d\n", err);
        return;
    }

    // Clear DMA buffer
    err = i2s_zero_dma_buffer(I2S_NUM_0);
    if (err != ESP_OK) {
        Serial.printf("Failed to zero DMA buffer: %d\n", err);
        return;
    }

    Serial.println("I2S initialized successfully");
}

// Initialize SD Card
void initializeSDCard() {
    Serial.println("SD Card functionality disabled");
}

// Read Microphone Data and Detect Wake Word
void readMicrophone() {
    int16_t buffer[BLOCK_SIZE];
    size_t bytes_read = 0;
    
    esp_err_t err = i2s_read(I2S_NUM_0, buffer, sizeof(buffer), &bytes_read, portMAX_DELAY);
    if (err != ESP_OK) {
        Serial.println("Failed to read I2S data");
        return;
    }

    // Print audio levels for debugging
    int32_t max_value = 0;
    for(int i = 0; i < BLOCK_SIZE; i++) {
        if(abs(buffer[i]) > max_value) {
            max_value = abs(buffer[i]);
        }
    }
    
    // Print audio level every second
    static unsigned long lastPrint = 0;
    if (millis() - lastPrint >= 1000) {
        Serial.printf("Audio Level: %d\n", max_value);
        lastPrint = millis();
    }

    // Send audio data to server if connected
    if(webSocket.isConnected()) {
        webSocket.sendBIN((uint8_t*)buffer, bytes_read);
    }
}

// Simple Energy-Based Wake Word Detection
bool detectWakeWord(int16_t sample) {
    // Calculate the absolute value of the sample
    int abs_sample = abs(sample);

    // If the sample exceeds the threshold, consider it as potential wake word
    if (abs_sample > WAKE_THRESHOLD) {
        return true;
    }
    return false;
}

// Start Recording
void startRecording() {
    if (isRecording) {
        Serial.println("Already recording!");
        return;
    }

    if (recording_buffer == nullptr) {
        Serial.println("Recording buffer not allocated!");
        return;
    }

    buffer_index = 0;
    isRecording = true;
    recordingStartTime = millis();
    Serial.println("Recording started...");
}

// Save Recording and send via WebSocket
void saveRecording() {
    if (!isRecording || buffer_index == 0) {
        Serial.println("No recording to save!");
        return;
    }

    // Send recording complete message
    StaticJsonDocument<200> doc;
    doc["type"] = "recording";
    doc["status"] = "complete";
    doc["samples"] = buffer_index;
    
    String jsonString;
    serializeJson(doc, jsonString);
    webSocket.sendTXT(jsonString);

    // Send the audio data in chunks
    const int CHUNK_SIZE = 1024;
    for (size_t i = 0; i < buffer_index; i += CHUNK_SIZE/2) {
        size_t remaining = buffer_index - i;
        size_t chunk = (remaining < CHUNK_SIZE/2) ? remaining : CHUNK_SIZE/2;
        webSocket.sendBIN((uint8_t*)&recording_buffer[i], chunk * sizeof(int16_t));
        
        // Small delay to prevent overwhelming the WebSocket
        delay(10);
    }

    // Reset recording state
    buffer_index = 0;
    isRecording = false;
    Serial.println("Recording complete and sent to server");
}

// Add new function to process commands
void processCommand() {
    if (!isRecording) return;
    
    // Send the recording to the server for command recognition
    saveRecording();
    
    // Reset for next command unless in complex task mode
    if (!complexTaskMode) {
        wakeWordDetected = false;
    }
}

// Initialize speech recognition
void initializeSpeechRecognition() {
    Serial.println("Initializing speech recognition...");

    // Initialize AFE with default config
    afe_config_t afe_config;
    afe_config.aec_init = true;
    afe_config.se_init = true;
    afe_config.vad_init = true;
    afe_config.wakenet_init = true;
    afe_config.voice_communication_init = false;
    afe_config.voice_communication_agc_init = false;
    afe_config.voice_communication_agc_gain = 15;
    afe_config.debug_init = false;
    afe_config.vad_mode = 3;  // VAD_MODE_3, where 3 is moderate sensitivity

    afe_data = afe_handle->create_from_config(&afe_config);
    if (!afe_data) {
        Serial.println("Failed to create AFE data");
        return;
    }



    // Initialize wake word detection
    if (afe_handle->set_wakenet(afe_data, NULL) != ESP_OK) {
        Serial.println("Failed to initialize wake word detection");
        return;
    }

    // Register commands
    const char *commands[] = {
        "turn on light",
        "turn off light",
        "start recording",
        "stop recording"
    };
    
    esp_mn_commands_clear();
    
    for (int i = 0; i < 4; i++) {
        char *cmd = (char *)commands[i];
        if (esp_mn_commands_add(i + 1, cmd) != ESP_OK) {
            Serial.printf("Failed to add command: %s\n", commands[i]);
            return;
        }
    }
    
    if (esp_mn_commands_update() != ESP_OK) {
        Serial.println("Failed to update commands");
        return;
    }

    Serial.println("Speech recognition initialized successfully");
}

void handleCommand(int command_id) {
    StaticJsonDocument<200> doc;
    doc["type"] = "command";
    
    switch(command_id) {
        case 1: // "turn on light"
            Serial.println("Command: Turn on light");
            doc["command"] = "turn_on_light";
            break;
            
        case 2: // "turn off light"
            Serial.println("Command: Turn off light");
            doc["command"] = "turn_off_light";
            break;
            
        case 3: // "start recording"
            doc["command"] = "start_recording";
            startRecording();
            break;
            
        case 4: // "stop recording"
            doc["command"] = "stop_recording";
            saveRecording();
            break;
            
        default:
            Serial.println("Unknown command");
            doc["command"] = "unknown";
            break;
    }
    
    // Send command to WebSocket server
    String jsonString;
    serializeJson(doc, jsonString);
    webSocket.sendTXT(jsonString);
}

// Add this function to periodically check WebSocket connection
void checkWebSocketConnection() {
    static unsigned long lastCheck = 0;
    if (millis() - lastCheck >= 5000) {  // Check every 5 seconds
        lastCheck = millis();
        if (!webSocket.isConnected()) {
            Serial.println("⚠️ WebSocket disconnected, attempting reconnect...");
            webSocket.disconnect();
            initializeWebSocket();
        }
    }
}

void enterLowPowerMode() {
    if (isRecording) {
        return; // Don't enter low power mode while recording
    }
    
    // Disable WiFi if not needed
    if (!webSocket.isConnected()) {
        WiFi.disconnect(true);
        WiFi.mode(WIFI_OFF);
    }
    
    // Configure wake-up sources
    esp_sleep_enable_timer_wakeup(5000000); // Wake up every 5 seconds
    
    // Enter light sleep
    esp_light_sleep_start();
}

void checkBatteryStatus() {
    // Add battery monitoring code here if using battery power
    // The XIAO ESP32S3 has a battery management system
}
