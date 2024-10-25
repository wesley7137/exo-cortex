const API_BASE_URL = "http://localhost:5000/api";

/**
 * Handles HTTP responses, throwing errors for non-OK responses.
 * @param {Response} response - The fetch response object.
 * @returns {Promise<any>} - Parsed JSON data.
 * @throws {Error} - If the response is not OK.
 */
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Something went wrong");
  }
  return response.json();
};
// Helper function to create fetch options with credentials
const createFetchOptions = (method, body = null) => {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", // This line ensures cookies are sent with every request
  };
  if (body) {
    options.body = JSON.stringify(body);
  }
  return options;
};

export const generateAIProfile = async (config) => {
  try {
    console.log("Sending request to generate AI profile:", config);
    const response = await fetch(
      `${API_BASE_URL}/ai-profile`,
      createFetchOptions("POST", config)
    );
    console.log("Response status:", response.status);
    const data = await handleResponse(response);
    console.log("Received AI profile:", data);
    return data;
  } catch (error) {
    console.error("Error generating AI profile:", error);
    throw error;
  }
};

export const fineTuneModel = async (modelId, fineTuneParams) => {
  try {
    const payload = { model_id: modelId, fine_tune_params: fineTuneParams };
    const response = await fetch(
      `${API_BASE_URL}/fine_tune_model`,
      createFetchOptions("POST", payload)
    );
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
    const response = await fetch(
      `${API_BASE_URL}/deploy_ai_assistant`,
      createFetchOptions("POST", payload)
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error deploying AI assistant:", error);
    throw error;
  }
};

export const trainPPOAgent = async (totalTimesteps = 10000) => {
  try {
    const payload = { total_timesteps: totalTimesteps };
    const response = await fetch(
      `${API_BASE_URL}/train_ppo`,
      createFetchOptions("POST", payload)
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error initiating PPO Agent training:", error);
    throw error;
  }
};

export const initializeGNNModel = async (params) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/init_gnn`,
      createFetchOptions("POST", params)
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error initializing GNN model:", error);
    throw error;
  }
};

export const registerUser = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(userData),
    });
    return handleResponse(response);
  } catch (error) {
    console.error("Error registering user:", error);
    throw error;
  }
};

export const loginUser = async (credentials) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/login`,
      createFetchOptions("POST", credentials)
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error logging in:", error);
    throw error;
  }
};

export const createUser = async (userData) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/users`,
      createFetchOptions("POST", userData)
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error creating user:", error);
    throw error;
  }
};

export const getPreferences = async () => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/users/me/preferences`,
      createFetchOptions("GET")
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error getting preferences:", error);
    throw error;
  }
};

export const setPreferences = async (preferences) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/users/me/preferences`,
      createFetchOptions("PUT", preferences)
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error setting preferences:", error);
    throw error;
  }
};

export const getUserAPIKeys = async () => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/users/me/api_keys`,
      createFetchOptions("GET")
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error getting user API keys:", error);
    throw error;
  }
};

export const updateUserAPIKeys = async (apiKeys) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/users/me/api_keys`,
      createFetchOptions("PUT", apiKeys)
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error updating user API keys:", error);
    throw error;
  }
};

export const listAIProfiles = async () => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/ai_profiles`,
      createFetchOptions("GET")
    );
    return handleResponse(response);
  } catch (error) {
    console.error("Error listing AI profiles:", error);
    throw error;
  }
};
