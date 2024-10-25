// frontend/RLAction.js

import React, { useState } from "react";
import {
  View,
  Text,
  Button,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import CONFIG from "./config";
import { trainPPOAgent } from "./services/api";

const RLAction = () => {
  const [action, setAction] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchRLAction = async () => {
    setLoading(true);
    try {
      // Assuming there's an endpoint to get RL actions; adjust as needed
      const response = await fetch(`${CONFIG.API_BASE_URL}/rl_action`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ state: [0.5, 0.5, 0.5] }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAction(data.action);
    } catch (error) {
      console.error("Error fetching RL action:", error);
      Alert.alert("Error", `Failed to fetch RL action: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTrainPPO = async () => {
    setLoading(true);
    try {
      const totalTimesteps = 10000; // Example parameter
      const result = await trainPPOAgent(totalTimesteps);
      Alert.alert("Success", result.message || "PPO Agent training initiated!");
      console.log("Training Response:", result);
    } catch (error) {
      console.error("Error initiating PPO Agent training:", error);
      Alert.alert(
        "Error",
        `Failed to initiate PPO Agent training: ${error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>RL Action Component</Text>
      <Button
        title="Get RL Action"
        onPress={fetchRLAction}
        disabled={loading}
      />
      {loading && <ActivityIndicator size="large" color="#0000ff" />}
      {action !== null && (
        <Text style={styles.actionText}>Action: {action}</Text>
      )}
      <View style={{ marginTop: 20 }}>
        <Button
          title="Train PPO Agent"
          onPress={handleTrainPPO}
          disabled={loading}
          color="#841584"
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: "#fff",
    flex: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
  },
  actionText: {
    fontSize: 18,
    marginTop: 20,
  },
});

export default RLAction;
