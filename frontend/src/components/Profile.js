import React, { useState, useEffect } from "react";
import {
  TextField,
  Button,
  Typography,
  Grid,
  CircularProgress,
  Snackbar,
  Alert,
} from "@mui/material";
import {
  getPreferences,
  setPreferences,
  getUserAPIKeys,
  updateUserAPIKeys,
} from "../services/api";
import "../styles/Theme.css";

function Profile() {
  const [preferences, setPreferencesState] = useState({
    personality: "",
    tasks: [],
    useCases: [],
  });

  const [apiKeys, setApiKeysState] = useState({
    openai_api_key: "",
    anthropic_api_key: "",
    google_api_key: "",
    huggingface_token: "",
    activeloop_token: "",
  });

  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const prefsData = await getPreferences();
        setPreferencesState(prefsData);

        const apiKeysData = await getUserAPIKeys();
        setApiKeysState(apiKeysData);
      } catch (error) {
        console.error(error);
        setSnackbar({
          open: true,
          message: "Failed to fetch profile data.",
          severity: "error",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handlePreferencesChange = (e) => {
    const { name, value } = e.target;
    setPreferencesState((prev) => ({ ...prev, [name]: value }));
  };

  const handleApiKeysChange = (e) => {
    const { name, value } = e.target;
    setApiKeysState((prev) => ({ ...prev, [name]: value }));
  };

  const handlePreferencesSubmit = async (e) => {
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
      console.error(error);
      setSnackbar({
        open: true,
        message: "Failed to update preferences.",
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApiKeysSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await updateUserAPIKeys(apiKeys);
      setSnackbar({
        open: true,
        message: "API keys updated successfully!",
        severity: "success",
      });
    } catch (error) {
      console.error(error);
      setSnackbar({
        open: true,
        message: "Failed to update API keys.",
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  if (loading) {
    return (
      <div
        className="card"
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "80vh",
        }}
      >
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div
      className="card"
      style={{ maxWidth: "600px", margin: "0 auto", padding: "20px" }}
    >
      <h2 className="card-header">Profile Customization</h2>
      <div style={{ marginBottom: "30px" }}>
        <form onSubmit={handlePreferencesSubmit}>
          <div className="form-group">
            <label htmlFor="personality">Personality Traits</label>
            <input
              id="personality"
              name="personality"
              value={preferences.personality}
              onChange={handlePreferencesChange}
              required
            />
          </div>
          <button type="submit" className="button" disabled={loading}>
            {loading ? "Saving..." : "Save Preferences"}
          </button>
        </form>
      </div>

      <h2 className="card-header">API Keys</h2>
      <form onSubmit={handleApiKeysSubmit}>
        {Object.entries(apiKeys).map(([key, value]) => (
          <div className="form-group" key={key}>
            <label htmlFor={key}>{key.replace(/_/g, " ").toUpperCase()}</label>
            <input
              id={key}
              name={key}
              type="password"
              value={value}
              onChange={handleApiKeysChange}
            />
          </div>
        ))}
        <button type="submit" className="button" disabled={loading}>
          {loading ? "Saving..." : "Save API Keys"}
        </button>
      </form>

      {snackbar.open && (
        <div
          className={`snackbar ${snackbar.severity}`}
          style={{
            position: "fixed",
            bottom: "20px",
            left: "50%",
            transform: "translateX(-50%)",
          }}
        >
          {snackbar.message}
        </div>
      )}
    </div>
  );
}

export default Profile;
