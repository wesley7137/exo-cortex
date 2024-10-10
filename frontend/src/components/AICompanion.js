import React, { useState, useEffect } from "react";
import { getPreferences, setPreferences } from "../services/api";

function AICompanion() {
  const [preferences, setPreferencesState] = useState({
    personality: "",
    tasks: [],
    useCases: [],
  });

  useEffect(() => {
    // Fetch user preferences from backend
    getPreferences()
      .then((data) => setPreferencesState(data))
      .catch((error) => console.error("Error fetching preferences:", error));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPreferencesState((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setPreferences(preferences)
      .then(() => alert("Preferences updated"))
      .catch((error) => console.error("Error updating preferences:", error));
  };

  return (
    <div>
      <h2>AI Companion Customization</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Personality Traits:
          <input
            type="text"
            name="personality"
            value={preferences.personality}
            onChange={handleChange}
          />
        </label>
        {/* Add more fields for tasks and use cases */}
        <button type="submit">Save Preferences</button>
      </form>
    </div>
  );
}

export default AICompanion;
