const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:5000/api";

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error);
  }
  return response.json();
};

export const generateAIProfile = async (config) => {
  try {
    console.log("Sending request to generate AI profile:", config);
    const response = await fetch(`${API_BASE_URL}/ai-profile`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    });
    console.log("Response status:", response.status);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log("Received AI profile:", data);
    return data;
  } catch (error) {
    console.error("Error generating AI profile:", error);
    throw error;
  }
};

export const fineTuneModel = async (modelId, fineTuneParams) => {
  try {
    const payload = {
      model_id: modelId,
      fine_tune_params: fineTuneParams,
    };
    const response = await fetch(`${API_BASE_URL}/fine-tune`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    return handleResponse(response);
  } catch (error) {
    console.error("Error fine-tuning model:", error);
    throw error;
  }
};

export const deployAIAssistant = async (profileId, deploymentParams) => {
  try {
    const payload = {
      profile_id: profileId,
      deployment_params: deploymentParams,
    };
    const response = await fetch(`${API_BASE_URL}/deploy`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    return handleResponse(response);
  } catch (error) {
    console.error("Error deploying AI assistant:", error);
    throw error;
  }
};

export const getPreferences = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/preferences`);
    return handleResponse(response);
  } catch (error) {
    console.error("Error getting preferences:", error);
    throw error;
  }
};

export const setPreferences = async (preferences) => {
  try {
    const response = await fetch(`${API_BASE_URL}/preferences`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(preferences),
    });
    return handleResponse(response);
  } catch (error) {
    console.error("Error setting preferences:", error);
    throw error;
  }
};

// Remove the default export since we're no longer using the Axios instance
