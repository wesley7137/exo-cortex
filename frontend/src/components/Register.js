import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser, loginUser } from "../services/api";
import styled, { keyframes } from "styled-components";

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #d3d3d3, #36454f);
  animation: ${fadeIn} 0.5s ease-in;
`;

const Card = styled.div`
  background: #2c3e50;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
  transform: perspective(1000px) rotateX(0deg);
  transition: transform 0.3s ease;
`;

const Title = styled.h2`
  color: #fff;
  margin-bottom: 1.5rem;
  text-align: center;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Input = styled.input`
  padding: 0.8rem;
  border: 1px solid #34495e;
  border-radius: 4px;
  font-size: 1rem;
  background-color: #34495e;
  color: #fff;
  transition: border-color 0.3s ease;

  &:focus {
    border-color: #a777e3;
    outline: none;
  }

  &::placeholder {
    color: #bdc3c7;
  }
`;

const Button = styled.button`
  padding: 0.8rem;
  background-color: #6e8efb;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.1s ease;
  width: 100%;

  &:hover {
    background-color: #5c7cfa;
  }

  &:active {
    transform: scale(0.98);
  }
`;

const ErrorMessage = styled.p`
  color: #ff4136;
  text-align: center;
  margin-top: 1rem;
`;

const Divider = styled.div`
  display: flex;
  align-items: center;
  text-align: center;
  margin: 1rem 0;
  color: #bdc3c7;

  &::before,
  &::after {
    content: "";
    flex: 1;
    border-bottom: 1px solid #bdc3c7;
  }

  &::before {
    margin-right: 0.5em;
  }

  &::after {
    margin-left: 0.5em;
  }
`;

const NavBar = styled.nav`
  display: flex;
  justify-content: space-between;
  padding: 1rem 2rem;
  background-color: transparent;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
`;

const NavLink = styled.a`
  color: #fff;
  text-decoration: none;
  margin: 0 1rem;
  font-size: 1rem;
`;

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await registerUser({ username, email, password });
      localStorage.setItem("token", response.token);
      navigate("/profile");
    } catch (err) {
      setError("Registration failed. Please try again.");
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await loginUser({ email, password });
      localStorage.setItem("token", response.token);
      navigate("/profile");
    } catch (err) {
      setError("Login failed. Please try again.");
    }
  };

  return (
    <Container>
      <Card>
        <Title>Register / Login</Title>
        <Form onSubmit={handleRegister}>
          <Input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit">Register</Button>
        </Form>
        <Divider>or</Divider>
        <Button onClick={handleLogin}>Login</Button>
        {error && <ErrorMessage>{error}</ErrorMessage>}
      </Card>
    </Container>
  );
}

export default Register;
