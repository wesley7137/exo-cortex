// frontend/config.js

const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:5000/api";

export { API_BASE_URL };

const config = {
  API_BASE_URL,
  // Add other configuration variables here as needed
};

export default config;
