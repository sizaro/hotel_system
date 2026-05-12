import { BrowserRouter, Routes, Route } from "react-router-dom";

/* Layout */
import PublicLayout from "./layouts/PublicLayout";

/* Pages */
import Home from "./pages/public/Home";
import Login from "./pages/public/Login";
import Register from "./pages/public/Register";
import About from "./pages/public/About";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* ================= PUBLIC AREA ================= */}
        <Route path="/" element={<PublicLayout />}>

          <Route index element={<Home />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="about" element={<About />} />

        </Route>

        {/* ================= DASHBOARD (TEMP SIMPLE) ================= */}
        <Route path="/dashboard" element={<Dashboard />} />

      </Routes>

    </BrowserRouter>
  );
}

export default App;