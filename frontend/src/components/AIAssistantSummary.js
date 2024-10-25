import React from "react";
import PropTypes from "prop-types";
import "../styles/Theme.css";

const AIAssistantSummary = ({ config, aiProfile, open, onClose }) => {
  if (!aiProfile || !open) {
    return null;
  }

  return (
    <div
      className="card"
      style={{ maxWidth: "800px", margin: "40px auto", padding: "20px" }}
    >
      <h2 className="card-header">AI Assistant Summary</h2>
      <div className="summary-content">
        <div className="summary-section">
          <h3>Configuration</h3>
          <ul>
            <li>Base Model: {config.baseModel}</li>
            <li>Personality: {config.personality}</li>
            <li>Primary Expertise: {config.primaryExpertise}</li>
            <li>Communication Style: {config.communicationStyle}</li>
            <li>Creativity Level: {config.creativityLevel}</li>
            <li>Response Length: {config.responseLength}</li>
            <li>Memory Modules: {config.memoryModules.join(", ")}</li>
            <li>Tool Integrations: {config.toolIntegrations.join(", ")}</li>
            <li>Execute Code: {config.executeCode ? "Yes" : "No"}</li>
            <li>Always On: {config.alwaysOn ? "Yes" : "No"}</li>
            <li>Ethical Boundaries: {config.ethicalBoundaries.join(", ")}</li>
            <li>
              Language Proficiency: {config.languageProficiency.join(", ")}
            </li>
            <li>
              Voice Interface: {config.voiceInterface ? "Enabled" : "Disabled"}
            </li>
            <li>Learning Rate: {config.learningRate}</li>
            <li>
              Speech-to-Text: {config.speechToText ? "Enabled" : "Disabled"}
            </li>
          </ul>
        </div>
        <div className="summary-section">
          <h3>AI Profile</h3>
          <ul>
            <li>AI Profile ID: {aiProfile.id}</li>
            <li>Base Model: {aiProfile.base_model}</li>
            <li>Always On: {aiProfile.always_on ? "Yes" : "No"}</li>
            <li>Communication Style: {aiProfile.communication_style}</li>
          </ul>
        </div>
      </div>
      <button className="button" onClick={onClose}>
        Close
      </button>
    </div>
  );
};

AIAssistantSummary.propTypes = {
  config: PropTypes.object.isRequired,
  aiProfile: PropTypes.object,
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default AIAssistantSummary;
