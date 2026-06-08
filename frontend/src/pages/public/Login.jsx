import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";

function Login() {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
  e.preventDefault();

  console.log("USERNAME:", username);
  console.log("PASSWORD:", password);

  const success = await login(username, password);

  if (success) {
    navigate("/dashboard");
  } else {
    alert("Invalid credentials");
  }
};

  return (
    <div>
      <h1>Login</h1>

      <form onSubmit={handleSubmit}>

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">Login</button>

      </form>
    </div>
  );
}

export default Login;