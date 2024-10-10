// AdvancedAICustomization.js

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
} from "@mui/material";
import {
  generateAIProfile,
  fineTuneModel,
  deployAIAssistant,
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
    learningRate: 50,
    speechToText: false,
  });

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
        // Define your fine-tuning parameters here
        learning_rate: config.learningRate,
        // Add other parameters as needed
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
        message: "Failed to fine-tune model.",
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
        // Define your deployment parameters here
        environment: "production",
        scaling: {
          min_instances: 1,
          max_instances: 5,
        },
        // Add other parameters as needed
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
        message: "Failed to deploy AI assistant.",
        severity: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCustomizeProfile = (key, value) => {
    setAIProfile((prev) => ({ ...prev, [key]: value }));
  };

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  if (showSummary) {
    return (
      <AIAssistantSummary
        config={config}
        aiProfile={aiProfile}
        onCustomize={handleCustomizeProfile}
      />
    );
  }

  return (
    <Card
      sx={{
        backgroundColor: "grey",
        width: "70vw",
        alignItems: "center",
        marginLeft: "auto",
        marginRight: "auto",
      }}
      className="mb-6"
    >
      <CardHeader title="Advanced AI Customization" />
      <CardContent>
        <div className="space-y-6">
          {/* Base Model Selection */}
          <div>
            <Typography variant="subtitle1" gutterBottom>
              Select Base Model
            </Typography>
            <Select
              fullWidth
              value={config.baseModel}
              onChange={(e) => handleConfigChange("baseModel", e.target.value)}
              displayEmpty
            >
              <MenuItem value="" disabled>
                Choose a base model
              </MenuItem>
              <MenuItem value="gpt4mini">GPT-4 Mini</MenuItem>
              <MenuItem value="llama3.2-3b">
                LLaMA 3.2 (3 billion parameters)
              </MenuItem>
              <MenuItem value="llama3.2-1b">
                LLaMA 3.2 (1 billion parameters)
              </MenuItem>
              <MenuItem value="mini-llava">Mini-LLaVA</MenuItem>
              <MenuItem value="qwen2.5-2b">
                Qwen 2.5 (2 billion parameters)
              </MenuItem>
            </Select>
          </div>

          {/* Personality and Expertise */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Typography variant="subtitle1" gutterBottom>
                Personality
              </Typography>
              <Select
                fullWidth
                value={config.personality}
                onChange={(e) =>
                  handleConfigChange("personality", e.target.value)
                }
                displayEmpty
              >
                <MenuItem value="" disabled>
                  Select personality
                </MenuItem>
                <MenuItem value="friendly">Friendly and Approachable</MenuItem>
                <MenuItem value="professional">
                  Professional and Formal
                </MenuItem>
                <MenuItem value="witty">Witty and Humorous</MenuItem>
                <MenuItem value="empathetic">
                  Empathetic and Supportive
                </MenuItem>
              </Select>
            </div>
            <div>
              <Typography variant="subtitle1" gutterBottom>
                Primary Expertise
              </Typography>
              <Select
                fullWidth
                value={config.primaryExpertise}
                onChange={(e) =>
                  handleConfigChange("primaryExpertise", e.target.value)
                }
                displayEmpty
              >
                <MenuItem value="" disabled>
                  Select primary expertise
                </MenuItem>
                <MenuItem value="general">General Knowledge</MenuItem>
                <MenuItem value="tech">Technology and Programming</MenuItem>
                <MenuItem value="health">Health and Wellness</MenuItem>
                <MenuItem value="finance">Finance and Economics</MenuItem>
                <MenuItem value="creative">Creative Writing</MenuItem>
                <MenuItem value="legal">Legal</MenuItem>
                <MenuItem value="scientific">Scientific Research</MenuItem>
              </Select>
            </div>
          </div>

          {/* Communication Style, Creativity, and Response Length Sliders */}
          <div className="space-y-4">
            <div>
              <Typography variant="subtitle1" gutterBottom>
                Communication Style
              </Typography>
              <Slider
                min={0}
                max={100}
                step={1}
                value={config.communicationStyle}
                onChange={(_, value) =>
                  handleConfigChange("communicationStyle", value)
                }
                valueLabelDisplay="auto"
              />
              <div className="flex justify-between mt-1">
                <Typography variant="caption">Concise</Typography>
                <Typography variant="caption">Detailed</Typography>
              </div>
            </div>
            <div>
              <Typography variant="subtitle1" gutterBottom>
                Creativity Level
              </Typography>
              <Slider
                min={0}
                max={100}
                step={1}
                value={config.creativityLevel}
                onChange={(_, value) =>
                  handleConfigChange("creativityLevel", value)
                }
                valueLabelDisplay="auto"
              />
              <div className="flex justify-between mt-1">
                <Typography variant="caption">Conservative</Typography>
                <Typography variant="caption">Highly Creative</Typography>
              </div>
            </div>
            <div>
              <Typography variant="subtitle1" gutterBottom>
                Preferred Response Length
              </Typography>
              <Slider
                min={0}
                max={100}
                step={1}
                value={config.responseLength}
                onChange={(_, value) =>
                  handleConfigChange("responseLength", value)
                }
                valueLabelDisplay="auto"
              />
              <div className="flex justify-between mt-1">
                <Typography variant="caption">Brief</Typography>
                <Typography variant="caption">Comprehensive</Typography>
              </div>
            </div>
          </div>

          {/* Memory Modules */}
          <div>
            <Typography variant="subtitle1" gutterBottom>
              Memory Modules (RAG)
            </Typography>
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.memoryModules.includes("regular")}
                  onChange={() =>
                    handleArrayConfigChange("memoryModules", "regular")
                  }
                />
              }
              label="Regular Memory"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.memoryModules.includes("legal")}
                  onChange={() =>
                    handleArrayConfigChange("memoryModules", "legal")
                  }
                />
              }
              label="Legal Database"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.memoryModules.includes("medical")}
                  onChange={() =>
                    handleArrayConfigChange("memoryModules", "medical")
                  }
                />
              }
              label="Medical Database"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.memoryModules.includes("scientific")}
                  onChange={() =>
                    handleArrayConfigChange("memoryModules", "scientific")
                  }
                />
              }
              label="Scientific Papers"
            />
          </div>

          {/* Tool Integrations */}
          <div>
            <Typography variant="subtitle1" gutterBottom>
              Tool Integrations
            </Typography>
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.toolIntegrations.includes("web-search")}
                  onChange={() =>
                    handleArrayConfigChange("toolIntegrations", "web-search")
                  }
                />
              }
              label="Web Search"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.toolIntegrations.includes("calculator")}
                  onChange={() =>
                    handleArrayConfigChange("toolIntegrations", "calculator")
                  }
                />
              }
              label="Calculator"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.toolIntegrations.includes("text-to-speech")}
                  onChange={() =>
                    handleArrayConfigChange(
                      "toolIntegrations",
                      "text-to-speech"
                    )
                  }
                />
              }
              label="Text-to-Speech"
            />
          </div>

          {/* Code Execution */}
          <FormControlLabel
            control={
              <Switch
                checked={config.executeCode}
                onChange={(e) =>
                  handleConfigChange("executeCode", e.target.checked)
                }
              />
            }
            label="Allow Code Execution"
          />

          {/* Always-On Mode */}
          <FormControlLabel
            control={
              <Switch
                checked={config.alwaysOn}
                onChange={(e) =>
                  handleConfigChange("alwaysOn", e.target.checked)
                }
              />
            }
            label="Always-On Mode (Second Brain)"
          />

          {/* Ethical Boundaries */}
          <div>
            <Typography variant="subtitle1" gutterBottom>
              Ethical Boundaries
            </Typography>
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.ethicalBoundaries.includes("no-harm")}
                  onChange={() =>
                    handleArrayConfigChange("ethicalBoundaries", "no-harm")
                  }
                />
              }
              label="Prevent Harmful Actions"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.ethicalBoundaries.includes("privacy")}
                  onChange={() =>
                    handleArrayConfigChange("ethicalBoundaries", "privacy")
                  }
                />
              }
              label="Respect Privacy"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.ethicalBoundaries.includes("truthful")}
                  onChange={() =>
                    handleArrayConfigChange("ethicalBoundaries", "truthful")
                  }
                />
              }
              label="Always Be Truthful"
            />
          </div>

          {/* Language Proficiency */}
          <div>
            <Typography variant="subtitle1" gutterBottom>
              Language Proficiency
            </Typography>
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.languageProficiency.includes("english")}
                  onChange={() =>
                    handleArrayConfigChange("languageProficiency", "english")
                  }
                />
              }
              label="English"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.languageProficiency.includes("spanish")}
                  onChange={() =>
                    handleArrayConfigChange("languageProficiency", "spanish")
                  }
                />
              }
              label="Spanish"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={config.languageProficiency.includes("mandarin")}
                  onChange={() =>
                    handleArrayConfigChange("languageProficiency", "mandarin")
                  }
                />
              }
              label="Mandarin"
            />
          </div>

          {/* Voice Interface */}
          <FormControlLabel
            control={
              <Switch
                checked={config.voiceInterface}
                onChange={(e) =>
                  handleConfigChange("voiceInterface", e.target.checked)
                }
              />
            }
            label="Enable Voice Interface"
          />

          {/* Learning Rate */}
          <div>
            <Typography variant="subtitle1" gutterBottom>
              Learning Rate
            </Typography>
            <Slider
              min={0}
              max={100}
              step={1}
              value={config.learningRate}
              onChange={(_, value) => handleConfigChange("learningRate", value)}
              valueLabelDisplay="auto"
            />
            <div className="flex justify-between mt-1">
              <Typography variant="caption">Stable</Typography>
              <Typography variant="caption">Highly Adaptive</Typography>
            </div>
          </div>

          {/* Speech-to-Text */}
          <FormControlLabel
            control={
              <Switch
                checked={config.speechToText}
                onChange={(e) =>
                  handleConfigChange("speechToText", e.target.checked)
                }
              />
            }
            label="Enable Speech-to-Text"
          />

          {/* Generate AI Profile */}
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleGenerateAIProfile}
            disabled={loading}
          >
            {loading ? (
              <CircularProgress size={24} />
            ) : (
              "Generate AI Assistant Profile"
            )}
          </Button>

          {/* Fine-tuning and Deployment */}
          <div className="flex space-x-4">
            <Button
              variant="contained"
              color="secondary"
              fullWidth
              onClick={handleFineTuneModel}
              disabled={loading || !aiProfile}
            >
              {loading ? <CircularProgress size={24} /> : "Fine-tune Model"}
            </Button>
            <Button
              variant="contained"
              color="secondary"
              fullWidth
              onClick={handleDeployAIAssistant}
              disabled={loading || !aiProfile}
            >
              {loading ? <CircularProgress size={24} /> : "Deploy AI Assistant"}
            </Button>
          </div>
        </div>
      </CardContent>

      <AIAssistantSummary
        config={config}
        aiProfile={aiProfile}
        open={showSummary}
        onClose={handleCloseSummary}
      />

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

export default AdvancedAICustomization;
