import React, { useState, useEffect } from "react";
import api, { generateAIProfile } from "../services/api";
import { useAuth0 } from "@auth0/auth0-react";
import axios from "axios";
function Profile() {
  const { user } = useAuth0();
  const [preferences, setPreferences] = useState({
    personality: "",
    tasks: [],
    useCases: [],
  });

  useEffect(() => {
    // Fetch user preferences from backend
    axios
      .get(`/api/users/${user.sub}/preferences`)
      .then((response) => setPreferences(response.data))
      .catch((error) => console.error(error));
  }, [user.sub]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPreferences((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios
      .post(`/api/users/${user.sub}/preferences`, preferences)
      .then((response) => alert("Preferences updated"))
      .catch((error) => console.error(error));
  };

  return (
    <div>
      <h2>Profile Customization</h2>
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

export default Profile;
