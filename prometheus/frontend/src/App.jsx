import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import NavBar from "./components/NavBar";
import Landing from "./pages/Landing";
import Projects from "./pages/Projects";
import Builder from "./pages/Builder";
import SystemControl from "./pages/SystemControl";

export default function App() {
  const location = useLocation();
  const showNav = location.pathname !== "/";

  return (
    <div className="app-root">
      {showNav && <NavBar />}
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/builder/:projectId" element={<Builder />} />
        <Route path="/system" element={<SystemControl />} />
      </Routes>
    </div>
  );
}
