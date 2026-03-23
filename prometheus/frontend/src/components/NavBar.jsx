import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

export default function NavBar() {
  const navigate = useNavigate();
  return (
    <nav className="navbar">
      <div className="navbar-logo" onClick={() => navigate("/")} style={{ cursor: "pointer" }}>
        <span className="neon-red" style={{ animation: "flicker 4s infinite", fontFamily: "var(--font-code)", fontSize: "1.1rem", fontWeight: 700, letterSpacing: "0.12em" }}>
          ⚡ PROMETHEUS
        </span>
      </div>
      <div className="navbar-links">
        <NavLink to="/projects" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>
          Projects
        </NavLink>
        <NavLink to="/system" className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}>
          System Control
        </NavLink>
      </div>
      <style>{`
        .navbar {
          display: flex;
          align-items: center;
          padding: 0 24px;
          height: 52px;
          background: var(--surface-1);
          border-bottom: 2px solid var(--red-bright);
          box-shadow: 0 2px 20px rgba(255,0,51,0.2);
          position: sticky;
          top: 0;
          z-index: 100;
          gap: 32px;
        }
        .navbar-logo { flex-shrink: 0; }
        .navbar-links { display: flex; gap: 8px; flex: 1; }
        .nav-link {
          color: var(--text-dim);
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          padding: 6px 12px;
          border-radius: var(--radius);
          transition: all 0.2s;
          text-decoration: none;
          position: relative;
        }
        .nav-link::after {
          content: "";
          position: absolute;
          bottom: -2px;
          left: 0;
          right: 0;
          height: 2px;
          background: var(--gold);
          transform: scaleX(0);
          transition: transform 0.2s;
        }
        .nav-link:hover { color: var(--text); }
        .nav-link.active { color: var(--gold); }
        .nav-link.active::after { transform: scaleX(1); }
      `}</style>
    </nav>
  );
}
