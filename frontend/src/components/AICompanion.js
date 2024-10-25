// frontend/components/AICompanion.js

import React, { useState, useEffect } from "react";
import { getPreferences, setPreferences } from "../services/api";
import {
  Card,
  CardContent,
  CardHeader,
  TextField,
  Button,
  Typography,
  Snackbar,
  Alert,
  FormControl,
  FormLabel,
  FormGroup,
  FormControlLabel,
  Checkbox,
  CircularProgress,
} from "@mui/material";

const AICompanion = () => {
  const [preferences, setPreferencesState] = useState({
    personality: "",
    tasks: [],
    useCases: [],
  });
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  useEffect(() => {
    // Fetch user preferences from backend
    const fetchPreferences = async () => {
      setLoading(true);
      try {
        const data = await getPreferences();
        setPreferencesState(data);
      } catch (error) {
        console.error("Error fetching preferences:", error);
        setSnackbar({
          open: true,
          message: `Failed to fetch preferences: ${error.message}`,
          severity: "error",
        });
      } finally {
        setLoading(false);
      }
    };
    fetchPreferences();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPreferencesState((prev) => ({ ...prev, [name]: value }));
  };

  const handleArrayChange = (e) => {
    const { name, value, checked } = e.target;
    setPreferencesState((prev) => ({
      ...prev,
      [name]: checked
        ? [...prev[name], value]
        : prev[name].filter((item) => item !== value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await setPreferences(preferences);
      setSnackbar({
        open: true,
        message: "Preferences updated successfully!",
        severity: "success",
      });
    } catch (error) {
      console.error("Error updating preferences:", error);
      setSnackbar({
        open: true,
        message: `Failed to update preferences: ${error.message}`,
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  return (
    <Card
      sx={{
        backgroundColor: "grey.100",
        width: "60vw",
        alignItems: "center",
        marginLeft: "auto",
        marginRight: "auto",
        marginTop: 4,
      }}
      className="mb-6"
    >
      <CardHeader title="AI Companion Preferences" />
      <CardContent>
        <form onSubmit={handleSubmit}>
          <Typography variant="subtitle1" gutterBottom>
            Personality Traits
          </Typography>
          <TextField
            fullWidth
            name="personality"
            value={preferences.personality}
            onChange={handleChange}
            placeholder="Enter personality traits"
            margin="normal"
            variant="outlined"
          />

          {/* Tasks */}
          <FormControl component="fieldset" margin="normal">
            <FormLabel component="legend">Tasks</FormLabel>
            <FormGroup row>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={preferences.tasks.includes("task1")}
                    onChange={handleArrayChange}
                    name="tasks"
                    value="task1"
                  />
                }
                label="Task 1"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={preferences.tasks.includes("task2")}
                    onChange={handleArrayChange}
                    name="tasks"
                    value="task2"
                  />
                }
                label="Task 2"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={preferences.tasks.includes("task3")}
                    onChange={handleArrayChange}
                    name="tasks"
                    value="task3"
                  />
                }
                label="Task 3"
              />
            </FormGroup>
          </FormControl>

          {/* Use Cases */}
          <FormControl component="fieldset" margin="normal">
            <FormLabel component="legend">Use Cases</FormLabel>
            <FormGroup row>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={preferences.useCases.includes("useCase1")}
                    onChange={handleArrayChange}
                    name="useCases"
                    value="useCase1"
                  />
                }
                label="Use Case 1"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={preferences.useCases.includes("useCase2")}
                    onChange={handleArrayChange}
                    name="useCases"
                    value="useCase2"
                  />
                }
                label="Use Case 2"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={preferences.useCases.includes("useCase3")}
                    onChange={handleArrayChange}
                    name="useCases"
                    value="useCase3"
                  />
                }
                label="Use Case 3"
              />
            </FormGroup>
          </FormControl>

          <Button
            variant="contained"
            color="primary"
            type="submit"
            fullWidth
            disabled={loading}
            size="large"
            sx={{ marginTop: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : "Save Preferences"}
          </Button>
        </form>
      </CardContent>

      {/* Snackbar for Notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Card>
  );
};

export default AICompanion;
