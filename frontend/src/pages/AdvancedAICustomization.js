// frontend/components/AdvancedAICustomization.js

import React, { useState } from "react";
import "../styles/Theme.css";
import {
  Card,
  CardContent,
  CardHeader,
  Button,
  Select,
  MenuItem,
  Slider,
  Switch,
  Checkbox,
  FormControlLabel,
  Typography,
  CircularProgress,
  Snackbar,
  Alert,
  Grid,
} from "@mui/material";
import { API_BASE_URL } from "../config";
import {
  generateAIProfile,
  fineTuneModel,
  deployAIAssistant,
  trainPPOAgent,
  initializeGNNModel,
} from "../services/api";
import AIAssistantSummary from "../components/AIAssistantSummary";

const AdvancedAICustomization = () => {
  const [config, setConfig] = useState({
    baseModel: "",
    personality: "",
    primaryExpertise: "",
    communicationStyle: 50,
    creativityLevel: 50,
    responseLength: 50,
    memoryModules: [],
    toolIntegrations: [],
    executeCode: false,
    alwaysOn: false,
    ethicalBoundaries: [],
    languageProficiency: [],
    voiceInterface: false,
    learningRate: 0.0003, // Changed to float
    speechToText: false,
  });
  const [error, setError] = useState("");

  const [showSummary, setShowSummary] = useState(false);
  const [aiProfile, setAIProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  const handleConfigChange = (key, value) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const handleArrayConfigChange = (key, value) => {
    setConfig((prev) => ({
      ...prev,
      [key]: prev[key].includes(value)
        ? prev[key].filter((item) => item !== value)
        : [...prev[key], value],
    }));
  };

  const handleGenerateAIProfile = async () => {
    setLoading(true);
    try {
      console.log("Generating AI profile with config:", config);
      const profile = await generateAIProfile(config);
      setAIProfile(profile);
      setShowSummary(true);
      setSnackbar({
        open: true,
        message: "AI Profile generated successfully!",
        severity: "success",
      });
    } catch (error) {
      console.error("Error generating AI profile:", error);
      setSnackbar({
        open: true,
        message: `Failed to generate AI profile: ${error.message}`,
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSummary = () => {
    setShowSummary(false);
  };

  const handleFineTuneModel = async () => {
    if (!aiProfile) {
      setSnackbar({
        open: true,
        message: "Please generate an AI profile first.",
        severity: "warning",
      });
      return;
    }
    setLoading(true);
    try {
      const fineTuneParams = {
        learningRate: config.learningRate,
        epochs: 3, // Example parameter
        batchSize: 16, // Example parameter
        datasetPath: "/path/to/dataset", // Replace with actual dataset path
      };
      const result = await fineTuneModel(aiProfile.id, fineTuneParams);
      setSnackbar({
        open: true,
        message: "Model fine-tuned successfully!",
        severity: "success",
      });
      console.log("Fine-Tune Result:", result);
    } catch (error) {
      console.error("Error fine-tuning model:", error);
      setSnackbar({
        open: true,
        message: `Failed to fine-tune model: ${error.message}`,
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeployAIAssistant = async () => {
    if (!aiProfile) {
      setSnackbar({
        open: true,
        message: "Please generate an AI profile first.",
        severity: "warning",
      });
      return;
    }
    setLoading(true);
    try {
      const deploymentParams = {
        environment: "production",
        scaling: {
          min_instances: 1,
          max_instances: 5,
        },
        customConfigurations: {}, // Add any custom configurations if needed
      };
      const deployment = await deployAIAssistant(
        aiProfile.id,
        deploymentParams
      );
      setSnackbar({
        open: true,
        message: "AI Assistant deployed successfully!",
        severity: "success",
      });
      console.log("Deployment Result:", deployment);
    } catch (error) {
      console.error("Error deploying AI assistant:", error);
      setSnackbar({
        open: true,
        message: `Failed to deploy AI assistant: ${error.message}`,
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTrainPPOAgent = async () => {
    setLoading(true);
    try {
      const totalTimesteps = 5000; // Example parameter
      const response = await trainPPOAgent(totalTimesteps);
      setSnackbar({
        open: true,
        message: "PPO Agent training initiated!",
        severity: "success",
      });
      console.log("Training Response:", response);
    } catch (error) {
      console.error("Error initiating PPO Agent training:", error);
      setSnackbar({
        open: true,
        message: `Failed to initiate PPO Agent training: ${error.message}`,
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInitializeGNNModel = async () => {
    setLoading(true);
    try {
      const gnnParams = {
        input_dim: 10,
        hidden_dim: 16,
        output_dim: 4,
      };
      const response = await initializeGNNModel(gnnParams);
      setSnackbar({
        open: true,
        message: "GNN Model initialization initiated!",
        severity: "success",
      });
      console.log("GNN Initialization Response:", response);
    } catch (error) {
      console.error("Error initializing GNN model:", error);
      setSnackbar({
        open: true,
        message: `Failed to initialize GNN model: ${error.message}`,
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  if (showSummary) {
    return (
      <AIAssistantSummary
        config={config}
        aiProfile={aiProfile}
        open={showSummary}
        onClose={handleCloseSummary}
      />
    );
  }

  return (
    <div
      className="card"
      style={{ maxWidth: "800px", margin: "40px auto", padding: "20px" }}
    >
      <h2 className="card-header">Advanced AI Customization</h2>
      <form>
        <div className="form-group">
          <label htmlFor="baseModel">Select Base Model</label>
          <select
            id="baseModel"
            value={config.baseModel}
            onChange={(e) => handleConfigChange("baseModel", e.target.value)}
          >
            <option value="" disabled>
              Choose a base model
            </option>
            <option value="gpt4mini">GPT-4 Mini</option>
            <option value="llama3.2-3b">LLaMA 3.2 (3B Params)</option>
            <option value="llama3.2-1b">LLaMA 3.2 (1B Params)</option>
            <option value="mini-llava">Mini-LLaVA</option>
            <option value="qwen2.5-2b">Qwen 2.5 (2B Params)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="personality">Personality</label>
          <select
            id="personality"
            value={config.personality}
            onChange={(e) => handleConfigChange("personality", e.target.value)}
          >
            <option value="" disabled>
              Select personality
            </option>
            <option value="friendly">Friendly and Approachable</option>
            <option value="professional">Professional and Formal</option>
            <option value="witty">Witty and Humorous</option>
            <option value="empathetic">Empathetic and Supportive</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="primaryExpertise">Primary Expertise</label>
          <select
            id="primaryExpertise"
            value={config.primaryExpertise}
            onChange={(e) =>
              handleConfigChange("primaryExpertise", e.target.value)
            }
          >
            <option value="" disabled>
              Select primary expertise
            </option>
            <option value="general">General Knowledge</option>
            <option value="tech">Technology and Programming</option>
            <option value="health">Health and Wellness</option>
            <option value="finance">Finance and Economics</option>
            <option value="creative">Creative Writing</option>
            <option value="legal">Legal</option>
            <option value="scientific">Scientific Research</option>
          </select>
        </div>

        <div className="form-group">
          <label>Communication Style</label>
          <input
            type="range"
            min="0"
            max="100"
            value={config.communicationStyle}
            onChange={(e) =>
              handleConfigChange("communicationStyle", parseInt(e.target.value))
            }
          />
          <div className="slider-labels">
            <span>Concise</span>
            <span>Detailed</span>
          </div>
        </div>

        <div className="form-group">
          <label>Creativity Level</label>
          <input
            type="range"
            min="0"
            max="100"
            value={config.creativityLevel}
            onChange={(e) =>
              handleConfigChange("creativityLevel", parseInt(e.target.value))
            }
          />
          <div className="slider-labels">
            <span>Conservative</span>
            <span>Highly Creative</span>
          </div>
        </div>

        <div className="form-group">
          <label>Preferred Response Length</label>
          <input
            type="range"
            min="0"
            max="100"
            value={config.responseLength}
            onChange={(e) =>
              handleConfigChange("responseLength", parseInt(e.target.value))
            }
          />
          <div className="slider-labels">
            <span>Brief</span>
            <span>Comprehensive</span>
          </div>
        </div>

        <div className="form-group">
          <label>Memory Modules (RAG)</label>
          <div className="checkbox-group">
            {[
              "Regular Memory",
              "Legal Database",
              "Medical Database",
              "Scientific Papers",
            ].map((module) => (
              <label key={module}>
                <input
                  type="checkbox"
                  checked={config.memoryModules.includes(
                    module.toLowerCase().replace(" ", "-")
                  )}
                  onChange={() =>
                    handleArrayConfigChange(
                      "memoryModules",
                      module.toLowerCase().replace(" ", "-")
                    )
                  }
                />
                {module}
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Tool Integrations</label>
          <div className="checkbox-group">
            {["Web Search", "Calculator", "Text-to-Speech"].map((tool) => (
              <label key={tool}>
                <input
                  type="checkbox"
                  checked={config.toolIntegrations.includes(
                    tool.toLowerCase().replace(/\s+/g, "-")
                  )}
                  onChange={() =>
                    handleArrayConfigChange(
                      "toolIntegrations",
                      tool.toLowerCase().replace(/\s+/g, "-")
                    )
                  }
                />
                {tool}
              </label>
            ))}
          </div>
        </div>
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={config.executeCode}
              onChange={(e) =>
                handleConfigChange("executeCode", e.target.checked)
              }
            />
            Allow Code Execution
          </label>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={config.alwaysOn}
              onChange={(e) => handleConfigChange("alwaysOn", e.target.checked)}
            />
            Always-On Mode (Second Brain)
          </label>
        </div>

        <div className="form-group">
          <label>Ethical Boundaries</label>
          <div className="checkbox-group">
            {[
              "Prevent Harmful Actions",
              "Respect Privacy",
              "Always Be Truthful",
            ].map((boundary) => (
              <label key={boundary}>
                <input
                  type="checkbox"
                  checked={config.ethicalBoundaries.includes(
                    boundary.toLowerCase().replace(" ", "-")
                  )}
                  onChange={() =>
                    handleArrayConfigChange(
                      "ethicalBoundaries",
                      boundary.toLowerCase().replace(" ", "-")
                    )
                  }
                />
                {boundary}
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Language Proficiency</label>
          <div className="checkbox-group">
            {["English", "Spanish", "Mandarin"].map((language) => (
              <label key={language}>
                <input
                  type="checkbox"
                  checked={config.languageProficiency.includes(
                    language.toLowerCase()
                  )}
                  onChange={() =>
                    handleArrayConfigChange(
                      "languageProficiency",
                      language.toLowerCase()
                    )
                  }
                />
                {language}
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={config.voiceInterface}
              onChange={(e) =>
                handleConfigChange("voiceInterface", e.target.checked)
              }
            />
            Enable Voice Interface
          </label>
        </div>

        <div className="form-group">
          <label>Learning Rate</label>
          <input
            type="range"
            min="0.0001"
            max="0.01"
            step="0.0001"
            value={config.learningRate}
            onChange={(e) =>
              handleConfigChange("learningRate", parseFloat(e.target.value))
            }
          />
          <div className="slider-labels">
            <span>Stable</span>
            <span>Highly Adaptive</span>
          </div>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={config.speechToText}
              onChange={(e) =>
                handleConfigChange("speechToText", e.target.checked)
              }
            />
            Enable Speech-to-Text
          </label>
        </div>

        <button
          type="button"
          className="button"
          onClick={handleGenerateAIProfile}
          disabled={loading}
        >
          {loading ? "Generating..." : "Generate AI Profile"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {showSummary && (
        <AIAssistantSummary
          config={config}
          aiProfile={aiProfile}
          open={showSummary}
          onClose={handleCloseSummary}
        />
      )}
    </div>
  );
};

export default AdvancedAICustomization;
