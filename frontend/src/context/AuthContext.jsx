import { createContext, useState, useEffect } from "react";
import axios from "axios";

export const AuthContext = createContext();

export function AuthProvider({ children }) {

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ================= LOGIN =================
  const login = async (username, password) => {
    try {

      await axios.post("http://127.0.0.1:8000/api/login/", {
        username,
        password,
      }, {
        withCredentials: true,
      });

      // After login → immediately fetch user
      await checkAuth();

      return true;

    } catch (err) {
      setUser(null);
      return false;
    }
  };

  // ================= CHECK AUTH (/me) =================
  const checkAuth = async () => {
    try {

      const res = await axios.get("http://127.0.0.1:8000/api/me/", {
        withCredentials: true,
      });

      setUser(res.data);

    } catch (err) {
      setUser(null);

    } finally {
      setLoading(false);
    }
  };

  // ================= LOGOUT =================
  const logout = async () => {
    try {

      await axios.post("http://127.0.0.1:8000/api/logout/", {}, {
        withCredentials: true,
      });

    } catch (err) {
      console.log(err);
    }

    setUser(null);
  };

  // ================= RUN ON APP START =================
  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}