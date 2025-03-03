import { useNavigate } from "react-router-dom";
import { useState, useContext } from "react";
import axios from "axios";
import { UserContext } from "../providers/UserContext";

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { setUser } = useContext(UserContext);

  const navigateToRegister = () => {
    navigate("/register");
  };
  const navigateToPredict = () => {
    navigate("/predict");
  };

  const setItemsInLocalStorage = (key, value) => {
    if (!key || !value) {
      return console.error("Cannot store in LS");
    }

    const valueToStore =
      typeof value !== "string" ? JSON.stringify(value) : value;
    localStorage.setItem(key, valueToStore);
  };

  const login = (e) => {
    e.preventDefault();
    axios
      .post("http://127.0.0.1:8887/login", {
        username: username,
        password: password,
      })
      .then((res) => {
        setItemsInLocalStorage("token", res.data.token);
        setUser(res.data.user);
        navigateToPredict();
      })
      .catch((e) => {
        console.log(e.message);
      });
  };

  return (
    <div className="bg-gray-50 flex items-center justify-center">
      <form
        onSubmit={login}
        className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm"
      >
        <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
          Login
        </h2>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <button
            type="submit"
            className="w-full py-3 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            Login
          </button>
        </div>
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{" "}
            <button
              onClick={navigateToRegister}
              className="text-indigo-600 hover:underline focus:outline-none"
            >
              Register here
            </button>
          </p>
        </div>
      </form>
    </div>
  );
};

export default Login;
