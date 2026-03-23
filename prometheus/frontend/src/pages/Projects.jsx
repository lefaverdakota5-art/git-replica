import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import StatusBadge from "../components/StatusBadge";

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [stats, setStats] = useState(null);
  const [creating, setCreating] = useState(false);
  const [newForm, setNewForm] = useState({ name: "", description: "", app_type: "api", framework: "fastapi" });
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    Promise.all([api.listProjects(), api.stats()])
      .then(([ps, st]) => { setProjects(ps); setStats(st); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const filtered = projects.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    (p.framework || "").toLowerCase().includes(search.toLowerCase())
  );

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newForm.name.trim()) return;
    setCreating(false);
    try {
      const p = await api.createProject(newForm);
      navigate(`/builder/${p.id}`);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this project?")) return;
    await api.deleteProject(id).catch(() => {});
    load();
  };

  return (
    <div style={{ padding: "28px 32px", maxWidth: 1200, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-code)", fontSize: "1.5rem", fontWeight: 700, color: "var(--red-bright)", letterSpacing: "0.05em" }}>
            MY PROJECTS
          </h1>
          {stats && (
            <p style={{ color: "var(--text-dim)", fontSize: "0.8rem" }}>
              {stats.projects} total · {stats.running} running · {stats.total_files} files
            </p>
          )}
        </div>
        <button className="cyber-btn primary" onClick={() => setCreating(true)}>⊕ New Project</button>
      </div>

      {/* New project modal */}
      {creating && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200 }}>
          <div className="cyber-card" style={{ width: 440, padding: 28 }}>
            <h2 style={{ marginBottom: 20, fontFamily: "var(--font-code)", color: "var(--red-bright)" }}>NEW PROJECT</h2>
            <form onSubmit={handleCreate}>
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: "block", fontSize: "0.7rem", textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 6 }}>Name</label>
                <input className="cyber-input" value={newForm.name} onChange={(e) => setNewForm({ ...newForm, name: e.target.value })} placeholder="my-awesome-app" required />
              </div>
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: "block", fontSize: "0.7rem", textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 6 }}>Description</label>
                <input className="cyber-input" value={newForm.description} onChange={(e) => setNewForm({ ...newForm, description: e.target.value })} placeholder="What does it do?" />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.7rem", textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 6 }}>Type</label>
                  <select className="cyber-input" value={newForm.app_type} onChange={(e) => setNewForm({ ...newForm, app_type: e.target.value })} style={{ cursor: "pointer" }}>
                    {["api","web","cli","fullstack","react","vue","django","node","nextjs","go"].map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "0.7rem", textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 6 }}>Framework</label>
                  <input className="cyber-input" value={newForm.framework} onChange={(e) => setNewForm({ ...newForm, framework: e.target.value })} placeholder="fastapi" />
                </div>
              </div>
              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
                <button type="button" className="cyber-btn" onClick={() => setCreating(false)}>Cancel</button>
                <button type="submit" className="cyber-btn primary">Create →</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Search */}
      <div style={{ marginBottom: 20 }}>
        <input className="cyber-input" placeholder="🔍 Search projects…" value={search} onChange={(e) => setSearch(e.target.value)} style={{ maxWidth: 360 }} />
      </div>

      {/* Project grid */}
      {loading ? (
        <div style={{ color: "var(--text-dim)", textAlign: "center", padding: 60 }}>Loading…</div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: "center", padding: 80 }}>
          <div style={{ fontSize: "3rem", marginBottom: 16 }}>⚡</div>
          <p style={{ color: "var(--text-dim)", fontSize: "1rem" }}>
            {search ? "No projects match your search." : "No projects yet. Create your first one!"}
          </p>
          {!search && <button className="cyber-btn primary" onClick={() => setCreating(true)} style={{ marginTop: 20 }}>⊕ New Project</button>}
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
          {filtered.map((p) => (
            <div key={p.id} className="cyber-card" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <h3 style={{ fontFamily: "var(--font-code)", fontSize: "0.95rem", fontWeight: 700, color: "var(--text)", marginRight: 8 }}>{p.name}</h3>
                <StatusBadge status={p.status || "stopped"} />
              </div>
              {p.description && <p style={{ fontSize: "0.78rem", color: "var(--text-dim)", lineHeight: 1.5 }}>{p.description}</p>}
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <span style={{ background: "rgba(255,0,51,0.1)", border: "1px solid rgba(255,0,51,0.3)", borderRadius: 4, padding: "2px 8px", fontSize: "0.68rem", color: "var(--red-bright)", fontFamily: "var(--font-code)" }}>{p.framework || p.app_type}</span>
                <span style={{ color: "var(--text-dim)", fontSize: "0.7rem", alignSelf: "center" }}>
                  {p.updated_at ? new Date(p.updated_at).toLocaleDateString() : ""}
                </span>
              </div>
              <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
                <button className="cyber-btn" style={{ flex: 1, justifyContent: "center" }} onClick={() => navigate(`/builder/${p.id}`)}>Open Builder</button>
                <button className="cyber-btn" style={{ color: "var(--red-bright)", borderColor: "rgba(255,0,51,0.3)" }} onClick={() => handleDelete(p.id)}>🗑</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
