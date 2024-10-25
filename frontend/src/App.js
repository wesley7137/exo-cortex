import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Register from "./components/Register";
import Profile from "./components/Profile";
import AICompanion from "./components/AICompanion";
import Navbar from "./components/Navbar";
import AdvancedAICustomization from "./pages/AdvancedAICustomization";
import Login from "./components/Login";

function ProtectedRoute({ children }) {
  const isAuthenticated = localStorage.getItem("token") !== null;

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <>
      <Navbar />
      <div className="container" style={{ marginTop: "100px" }}>
        <Routes>
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ai"
            element={
              <ProtectedRoute>
                <AdvancedAICustomization />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
