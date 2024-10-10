// frontend/RLAction.js
import React, { useState } from "react";
import { View, Text, Button, StyleSheet } from "react-native";
import CONFIG from "./config";

const RLAction = () => {
  const [action, setAction] = useState(null);

  const fetchRLAction = async () => {
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/rl_action`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ state: [0.5, 0.5, 0.5] }),
      });
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setAction(data.action);
    } catch (error) {
      console.error("Error fetching RL action:", error);
    }
  };

  return (
    <View style={styles.container}>
      <Text>RL Action Component</Text>
      <Button title="Get RL Action" onPress={fetchRLAction} />
      {action !== null && <Text>Action: {action}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: "#fff",
  },
});

export default RLAction;
