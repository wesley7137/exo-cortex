import React from "react";
import { useAuth0 } from "@auth0/auth0-react";

function Register() {
  const { loginWithRedirect } = useAuth0();

  return (
    <div>
      <h2>Register / Login</h2>
      <button onClick={() => loginWithRedirect()}>
        Login/Register with Auth0
      </button>
    </div>
  );
}

export default Register;
