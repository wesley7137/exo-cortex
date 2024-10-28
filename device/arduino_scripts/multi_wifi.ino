#include <WiFi.h>

// Define the primary Wi-Fi credentials (e.g., home Wi-Fi)
const char* primary_ssid = "PrimaryWiFiSSID";
const char* primary_password = "PrimaryWiFiPassword";

// Define the secondary Wi-Fi credentials (your phone's hotspot)
const char* secondary_ssid = "YourPhoneHotspotSSID";
const char* secondary_password = "YourHotspotPassword";

// Function to attempt Wi-Fi connection with a timeout
bool connectToWiFi(const char* ssid, const char* password, unsigned long timeout = 10000) {
  WiFi.begin(ssid, password);
  unsigned long startTime = millis();
  Serial.print("Connecting to ");
  Serial.print(ssid);
  
  // Loop until connected or timeout occurs
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - startTime > timeout) {
      Serial.println("\nConnection timed out.");
      return false;  // Failed to connect within the timeout
    }
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  return true;
}

void setup() {
  Serial.begin(115200);

  // Try connecting to the primary Wi-Fi
  if (!connectToWiFi(primary_ssid, primary_password)) {
    // If connection to primary fails, try connecting to the secondary (phone's hotspot)
    Serial.println("Attempting to connect to secondary Wi-Fi (Phone Hotspot)...");
    if (!connectToWiFi(secondary_ssid, secondary_password)) {
      Serial.println("Failed to connect to both Wi-Fi networks.");
    }
  }
}

void loop() {
  // Your code here (main loop)
}
