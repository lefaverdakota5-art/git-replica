import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

const SUGGESTIONS = [
  { label: "SaaS App with auth + dashboard", prompt: "Build a SaaS app with user authentication, dashboard, and subscription management" },
  { label: "REST API with CRUD endpoints", prompt: "Create a REST API with full CRUD endpoints, validation, and error handling" },
  { label: "Real-time chat with WebSockets", prompt: "Build a real-time chat application using WebSockets with rooms and users" },
  { label: "CLI tool with subcommands", prompt: "Create a CLI tool with multiple subcommands, flags, and rich terminal output" },
  { label: "Full-stack blog with CMS", prompt: "Build a full-stack blog with CMS, markdown support, and admin panel" },
  { label: "E-commerce with payments", prompt: "Create an e-commerce platform with product catalog, cart, and payment integration" },
];

export default function Landing() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [recentProjects, setRecentProjects] = useState([]);
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.listProjects().then((ps) => setRecentProjects(ps.slice(-5).reverse())).catch(() => {});
    api.stats().then(setStats).catch(() => {});
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    try {
      const appName = prompt.replace(/[^a-z0-9]/gi, "-").toLowerCase().slice(0, 20) + "-" + Date.now().toString(36);
      const project = await api.createProject({
        name: appName,
        description: prompt,
        framework: "fastapi",
        app_type: "api",
      });
      navigate(`/builder/${project.id}`);
    } catch (e) {
      alert("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", position: "relative", overflow: "hidden" }}>
      {/* Scanline overlay */}
      <div style={{
        position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0,
        background: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)",
      }} />

      <div style={{ position: "relative", zIndex: 1, maxWidth: 900, margin: "0 auto", padding: "60px 24px 40px" }}>

        {/* Hero */}
        <div style={{ textAlign: "center", marginBottom: 56 }}>
          <h1 style={{
            fontFamily: "var(--font-code)",
            fontSize: "clamp(2.5rem, 8vw, 5rem)",
            fontWeight: 700,
            letterSpacing: "0.15em",
            animation: "flicker 5s infinite",
            color: "var(--red-bright)",
            textShadow: "0 0 20px rgba(255,0,51,0.5), 0 0 60px rgba(255,0,51,0.2)",
            marginBottom: 12,
          }}>
            PROMETHEUS
          </h1>
          <p style={{ fontSize: "1.1rem", color: "var(--text-dim)", letterSpacing: "0.08em", marginBottom: 4 }}>
            The <span className="neon-gold">Ultimate</span> Development Platform
          </p>
          <p style={{ fontSize: "0.8rem", color: "var(--text-dim)", opacity: 0.6 }}>
            Build faster than thought. Deploy in seconds.
          </p>
        </div>

        {/* Stats */}
        {stats && (
          <div style={{ display: "flex", justifyContent: "center", gap: 40, marginBottom: 48 }}>
            {[
              { label: "Frameworks", value: stats.frameworks_supported },
              { label: "Snippets", value: stats.snippets_available + "+" },
              { label: "Languages", value: stats.languages_supported },
              { label: "Projects", value: stats.projects },
            ].map((s) => (
              <div key={s.label} style={{ textAlign: "center" }}>
                <div style={{ fontFamily: "var(--font-code)", fontSize: "1.8rem", fontWeight: 700, color: "var(--gold)" }}>{s.value}</div>
                <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--text-dim)" }}>{s.label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Main input */}
        <div className="cyber-card" style={{ marginBottom: 32 }}>
          <label style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--text-dim)", display: "block", marginBottom: 10 }}>
            What do you want to build?
          </label>
          <textarea
            className="cyber-input"
            rows={3}
            placeholder="Describe your app… e.g. 'A REST API for managing tasks with user authentication'"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && e.ctrlKey) handleGenerate(); }}
            style={{ resize: "vertical", fontFamily: "var(--font-ui)" }}
          />
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 12, gap: 10 }}>
            <button className="cyber-btn" onClick={() => navigate("/projects")}>Browse Projects</button>
            <button
              className="cyber-btn primary"
              onClick={handleGenerate}
              disabled={loading || !prompt.trim()}
            >
              {loading ? "⚡ Creating…" : "⚡ Generate"}
            </button>
          </div>
        </div>

        {/* Suggestion cards */}
        <div style={{ marginBottom: 48 }}>
          <p style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--text-dim)", marginBottom: 14 }}>
            Or try a template →
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 12 }}>
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                className="cyber-card"
                onClick={() => setPrompt(s.prompt)}
                style={{
                  background: "var(--surface-1)",
                  border: "1px solid var(--border)",
                  cursor: "pointer",
                  textAlign: "left",
                  padding: "14px 16px",
                  color: "var(--text)",
                  transition: "all 0.2s",
                  borderRadius: "var(--radius)",
                }}
                onMouseOver={(e) => { e.currentTarget.style.borderColor = "rgba(255,215,0,0.5)"; e.currentTarget.style.color = "var(--gold)"; }}
                onMouseOut={(e) => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.color = "var(--text)"; }}
              >
                <span style={{ fontSize: "0.82rem" }}>{s.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Recent projects */}
        {recentProjects.length > 0 && (
          <div>
            <p style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--text-dim)", marginBottom: 14 }}>
              Recent projects →
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {recentProjects.map((p) => (
                <a
                  key={p.id}
                  href={`/builder/${p.id}`}
                  className="cyber-card"
                  style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", textDecoration: "none" }}
                >
                  <span style={{ fontWeight: 600, color: "var(--text)" }}>{p.name}</span>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-dim)", fontFamily: "var(--font-code)" }}>
                    {p.framework} · {new Date(p.updated_at).toLocaleDateString()}
                  </span>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
