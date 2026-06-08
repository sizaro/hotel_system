import { useState } from "react";
import { Link } from "react-router-dom";

function Navbar() {
  const [open, setOpen] = useState(false);

  const toggleMenu = () => setOpen(!open);

  return (
    <nav className="bg-gray-900 text-white px-6 py-4 flex justify-between items-center relative">

      {/* LOGO */}
      <h2 className="text-xl font-sm">Hotel System</h2>

      {/* DESKTOP LINKS */}
      <div className="hidden md:flex gap-6 items-center">
        <Link to="/" className="hover:text-blue-400">Home</Link>
        <Link to="/about" className="hover:text-blue-400">About</Link>
        <Link to="/contact" className="hover:text-blue-400">Contact</Link>

        <Link
          to="/login"
          className="bg-blue-500 px-4 py-1 rounded hover:bg-blue-600"
        >
          Login
        </Link>
      </div>

      {/* HAMBURGER ICON */}
      <button
        onClick={toggleMenu}
        className="md:hidden text-2xl z-50"
      >
        {open ? "✕" : "☰"}
      </button>

      {/* MOBILE MENU OVERLAY */}
      <div
        className={`fixed top-0 right-0 h-full w-2/3 bg-gray-950 text-white flex flex-col gap-6 p-8 transform transition-transform duration-300 md:hidden
        ${open ? "translate-x-0" : "translate-x-full"}`}
      >
        <Link onClick={toggleMenu} to="/">Home</Link>
        <Link onClick={toggleMenu} to="/about">About</Link>
        <Link onClick={toggleMenu} to="/contact">Contact</Link>

        <Link
          onClick={toggleMenu}
          to="/login"
          className="bg-blue-500 px-4 py-2 rounded text-center"
        >
          Login
        </Link>
      </div>

    </nav>
  );
}

export default Navbar;