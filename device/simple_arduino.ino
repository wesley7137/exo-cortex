#include <DFRobot_ASR.h>
#include <WiFi.h>
#include <HTTPClient.h>

DFRobot_ASR asr;  // Create ASR object

// Configuration
const char* primary_ssid = "17k2.5";
const char* primary_password = "9852587137";
const char* secondary_ssid = "iPhone (14)";
const char* secondary_password = "9852587137";
const char* serverUrl = "https://server.intelliroute-ai.com/upload";

// Status LEDs
const int wifiStatusLED = 14;
const int audioStatusLED = 15;
const int commandStatusLED = 13;

bool isListeningMode = false;
unsigned long lastAudioTime = 0;
const int audioInterval = 100;


// Function prototypes
// At the top with other declarations, keep the default argument here
bool connectToWiFi(const char* ssid, const char* password, unsigned long timeout = 10000);
void handleCommand(int command);
void sendAudioData();

void setup() {
    Serial.begin(9600);
    
    // Initialize LEDs
    pinMode(wifiStatusLED, OUTPUT);
    pinMode(audioStatusLED, OUTPUT);
    pinMode(commandStatusLED, OUTPUT);
    
    digitalWrite(wifiStatusLED, LOW);
    digitalWrite(audioStatusLED, LOW);
    digitalWrite(commandStatusLED, LOW);
    
    // Initialize WiFi
    if (!connectToWiFi(primary_ssid, primary_password)) {
        if (!connectToWiFi(secondary_ssid, secondary_password)) {
            Serial.println("Failed to connect to both WiFi networks.");
        }
    }

    // Initialize ASR module in LOOP mode
    asr.begin(asr.LOOP);
    
    // Add voice commands
    asr.addCommand("hey finn", 0);          // Wake word
    asr.addCommand("start listening", 1);    // Start command
    asr.addCommand("stop listening", 2);     // Stop command
    asr.addCommand("send audio", 3);         // Send audio command
    asr.addCommand("pause", 4);              // Pause command

    // Start recognition
    asr.start();
    Serial.println("Speech Recognition Started");
    
    digitalWrite(audioStatusLED, HIGH);
}

void loop() {
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        digitalWrite(wifiStatusLED, LOW);
        Serial.println("WiFi connection lost. Attempting to reconnect...");
        
        if (!connectToWiFi(primary_ssid, primary_password, 5000)) {
            if (!connectToWiFi(secondary_ssid, secondary_password, 5000)) {
                Serial.println("Failed to reconnect to any network.");
                delay(5000);
                return;
            }
        }
    }

    // Read voice commands
    int result = asr.read();
    if (result != -1) {
        digitalWrite(commandStatusLED, HIGH);
        handleCommand(result);
        digitalWrite(commandStatusLED, LOW);
    }

    // Handle continuous audio if in listening mode
    if (isListeningMode) {
        if (millis() - lastAudioTime >= audioInterval) {
            sendAudioData();
            lastAudioTime = millis();
        }
    }
}

// In the function definition, remove the default argument
bool connectToWiFi(const char* ssid, const char* password, unsigned long timeout) {
    WiFi.begin(ssid, password);
    unsigned long startTime = millis();
    Serial.print("Connecting to ");
    Serial.print(ssid);
    
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - startTime > timeout) {
            Serial.println("\nConnection timed out.");
            digitalWrite(wifiStatusLED, LOW);
            return false;
        }
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\nConnected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(wifiStatusLED, HIGH);
    return true;
}
void handleCommand(int command) {
    switch(command) {
        case 1: // "start listening"
            Serial.println("Starting audio stream");
            isListeningMode = true;
            lastAudioTime = millis();
            break;
            
        case 2: // "stop listening"
            Serial.println("Stopping audio stream");
            isListeningMode = false;
            break;
            
        case 3: // "send audio"
            Serial.println("Sending audio snippet");
            sendAudioData();
            break;
            
        case 4: // "pause"
            Serial.println("Pausing audio operations");
            isListeningMode = false;
            break;
    }
}

void sendAudioData() {
    if (WiFi.status() != WL_CONNECTED) return;

    digitalWrite(audioStatusLED, HIGH);
    
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "audio/raw");
    
    // Note: The DFRobot_ASR library doesn't provide direct access to audio data
    // You might need to implement additional functionality or use a different module
    // for actual audio streaming
    
    http.end();
    digitalWrite(audioStatusLED, LOW);
}
