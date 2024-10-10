import React from "react";
import { Routes, Route } from "react-router-dom";
import Register from "./components/Register";
import Profile from "./components/Profile";
import AICompanion from "./components/AICompanion";
import Navbar from "./components/Navbar";
import AdvancedAICustomization from "./pages/AdvancedAICustomization";

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<Profile />} />
        <Route
          path="/ai"
          element={
            <>
              <AdvancedAICustomization />
              <AICompanion />
            </>
          }
        />
        <Route path="*" element={<Register />} />
      </Routes>
    </>
  );
}

export default App;
