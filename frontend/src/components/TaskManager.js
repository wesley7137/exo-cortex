// frontend/TaskManager.js

import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import CONFIG from "../config";

const TaskManager = () => {
  const [tasks, setTasks] = useState([]);
  const [taskInput, setTaskInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/tasks`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // Assuming data is an object with task IDs as keys
      const formattedTasks = Object.entries(data).map(([id, task]) => ({
        id,
        ...task,
      }));
      setTasks(formattedTasks);
    } catch (error) {
      console.error("Error fetching tasks:", error);
      Alert.alert("Error", `Failed to fetch tasks: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const addTask = async () => {
    if (taskInput.trim() === "") return;
    setLoading(true);
    try {
      const payload = {
        description: taskInput.trim(),
      };
      const response = await fetch(`${CONFIG.API_BASE_URL}/tasks`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setTaskInput("");
      fetchTasks(); // Refresh the task list
      Alert.alert("Success", "Task added successfully!");
    } catch (error) {
      console.error("Error adding task:", error);
      Alert.alert("Error", `Failed to add task: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Task Manager</Text>
      <TextInput
        style={styles.input}
        placeholder="Add a new task"
        value={taskInput}
        onChangeText={setTaskInput}
      />
      <Button title="Add Task" onPress={addTask} disabled={loading} />
      {loading && <ActivityIndicator size="large" color="#0000ff" />}
      <FlatList
        data={tasks}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.taskItem}>
            <Text style={styles.taskText}>
              {item.description} - {item.status}
            </Text>
          </View>
        )}
        style={{ marginTop: 20 }}
      />
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
    marginBottom: 10,
  },
  input: {
    height: 40,
    borderColor: "gray",
    borderWidth: 1,
    marginBottom: 10,
    paddingHorizontal: 10,
  },
  taskItem: {
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#ccc",
  },
  taskText: {
    fontSize: 16,
  },
});

export default TaskManager;
