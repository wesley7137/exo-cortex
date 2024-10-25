import React from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";

const NavContainer = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #2c3e50;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
`;

const NavLink = styled(Link)`
  color: #fff;
  text-decoration: none;
  margin: 0 1rem;
  font-size: 1rem;
  transition: color 0.3s ease;

  &:hover {
    color: #6e8efb;
  }
`;

const NavButton = styled.button`
  padding: 0.5rem 1rem;
  background-color: #6e8efb;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #5c7cfa;
  }
`;

function Navbar() {
  const navigate = useNavigate();
  const isAuthenticated = localStorage.getItem("token") !== null;

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <NavContainer>
      <div>
        <NavLink to="/">Home</NavLink>
        {isAuthenticated && (
          <>
            <NavLink to="/profile">Profile</NavLink>
            <NavLink to="/ai">AI Companion</NavLink>
          </>
        )}
      </div>
      <div>
        {isAuthenticated ? (
          <NavButton onClick={handleLogout}>Logout</NavButton>
        ) : (
          <NavLink to="/login">Login/Register</NavLink>
        )}
      </div>
    </NavContainer>
  );
}

export default Navbar;
