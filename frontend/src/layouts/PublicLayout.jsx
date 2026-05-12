import { Outlet } from "react-router-dom";
import Navbar from "../components/public/Navbar";
import Footer from "../components/public/Footer";

function PublicLayout() {
  return (
    <div>

      {/* TOP NAVBAR */}
      <Navbar />

      {/* PAGE CONTENT (CHANGES PER ROUTE) */}
      <main>
        <Outlet />
      </main>

      {/* FOOTER */}
      <Footer />

    </div>
  );
}

export default PublicLayout;