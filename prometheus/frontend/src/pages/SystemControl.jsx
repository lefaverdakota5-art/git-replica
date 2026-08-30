import React, { useState, useEffect } from "react";
import api from "../api";
import Terminal from "../components/Terminal";
import {
  getEditorSettings,
  getStoredApiBaseUrl,
  isNativeShell,
  normalizeApiBaseUrl,
  setPersistedEditorSettings,
  setStoredApiBaseUrl,
} from "../config";

const TABS = ["Overview", "Generator", "Completion", "Packages", "Terminal", "Settings"];

export default function SystemControl() {
  const [tab, setTab] = useState("Overview");
  const [stats, setStats] = useState(null);
  const [genPrompt, setGenPrompt] = useState("");
  const [genLang, setGenLang] = useState("python");
  const [genResult, setGenResult] = useState("");
  const [genLoading, setGenLoading] = useState(false);
  const [complCode, setComplCode] = useState("");
  const [complLang, setComplLang] = useState("python");
  const [completions, setCompletions] = useState([]);
  const [complLoading, setComplLoading] = useState(false);
  const [pkgInput, setPkgInput] = useState("");
  const [pkgOutput, setPkgOutput] = useState("");
  const [termOutput, setTermOutput] = useState("");
  const [termProjectId, setTermProjectId] = useState("");
  const [projects, setProjects] = useState([]);
  const [editorSettings, setEditorSettings] = useState(() => getEditorSettings());
  const [apiBaseInput, setApiBaseInput] = useState(() => getStoredApiBaseUrl());
  const [settingsNotice, setSettingsNotice] = useState("");
  const [backendCheck, setBackendCheck] = useState({ status: "idle", message: "" });

  useEffect(() => {
    api.stats().then(setStats).catch(() => {});
    api.listProjects().then(setProjects).catch(() => {});
    setEditorSettings(getEditorSettings());
    setApiBaseInput(getStoredApiBaseUrl());
  }, []);

  const handleGenerate = async () => {
    if (!genPrompt.trim()) return;
    setGenLoading(true);
    try {
      const r = await api.generate(genPrompt, genLang);
      setGenResult(r.code);
    } catch (e) {
      setGenResult("Error: " + e.message);
    } finally {
      setGenLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!complCode.trim()) return;
    setComplLoading(true);
    try {
      const r = await api.complete(complCode, complLang, 0);
      setCompletions(r.completions || []);
    } catch (_) {
      setCompletions([]);
    } finally {
      setComplLoading(false);
    }
  };

  const handleInstallPkg = async () => {
    if (!pkgInput.trim()) return;
    const pkgs = pkgInput.trim().split(/[\s,]+/).filter(Boolean);
    setPkgOutput("Installing…");
    try {
      const r = await api.installPackages("_global_", pkgs, "pip").catch(async () => ({
        output: `Would run: pip install ${pkgs.join(" ")}`,
        success: false,
      }));
      setPkgOutput(r.output);
    } catch (e) {
      setPkgOutput("Error: " + e.message);
    }
  };

  const handleTermCmd = async (cmd) => {
    if (!termProjectId) {
      setTermOutput((p) => p + `$ ${cmd}\n[No project selected]\n`);
      return;
    }
    try {
      const r = await api.execCommand(termProjectId, cmd);
      setTermOutput((p) => p + `$ ${cmd}\n${r.output}\n`);
    } catch (e) {
      setTermOutput((p) => p + `Error: ${e.message}\n`);
    }
  };

  const handleSaveSettings = () => {
    setPersistedEditorSettings(editorSettings);
    const normalized = setStoredApiBaseUrl(apiBaseInput);
    setApiBaseInput(normalized);
    setSettingsNotice(normalized
      ? "Saved editor preferences and backend URL."
      : "Saved editor preferences. The web build will keep using same-origin /api routes.");
    setBackendCheck({ status: "idle", message: "" });
  };

  const handleCheckBackend = async () => {
    const normalized = normalizeApiBaseUrl(apiBaseInput);
    if (!normalized) {
      setBackendCheck({ status: "error", message: "Enter the full backend origin first, for example https://your-server.example.com:8000" });
      return;
    }
    setBackendCheck({ status: "checking", message: "Checking backend…" });
    try {
      const res = await fetch(`${normalized}/api/health`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const body = await res.json();
      setBackendCheck({ status: "ok", message: `Connected to ${body.service || "backend"} (${body.status || "ok"}).` });
    } catch (error) {
      setBackendCheck({ status: "error", message: `Could not reach ${normalized}/api/health: ${error.message}` });
    }
  };

  return (
    <div style={{ padding: "28px 32px", maxWidth: 1100, margin: "0 auto" }}>
      <h1
        style={{
          fontFamily: "var(--font-code)",
          fontSize: "1.5rem",
          fontWeight: 700,
          letterSpacing: "0.12em",
          marginBottom: 4,
          color: "var(--red-bright)",
          textShadow: "0 0 15px rgba(255,0,51,0.4)",
        }}
      >
        ⚙ SYSTEM CONTROL
      </h1>
      <p style={{ color: "var(--text-dim)", fontSize: "0.8rem", marginBottom: 28 }}>
        Prometheus AI Engine · Local Code Intelligence · No external APIs
      </p>

      <div style={{ display: "flex", gap: 4, marginBottom: 24, borderBottom: "1px solid var(--border)", paddingBottom: 0, flexWrap: "wrap" }}>
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              background: tab === t ? "var(--surface-2)" : "transparent",
              border: "1px solid " + (tab === t ? "var(--border)" : "transparent"),
              borderBottom: tab === t ? "2px solid var(--red-bright)" : "1px solid transparent",
              color: tab === t ? "var(--text)" : "var(--text-dim)",
              padding: "8px 16px",
              fontSize: "0.78rem",
              fontWeight: 600,
              cursor: "pointer",
              borderRadius: "4px 4px 0 0",
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              transition: "all 0.2s",
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Overview" && (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 16, marginBottom: 24 }}>
            {stats && [
              { label: "Projects", value: stats.projects, icon: "📦" },
              { label: "Running", value: stats.running, icon: "▶" },
              { label: "Total Files", value: stats.total_files, icon: "📄" },
              { label: "Frameworks", value: stats.frameworks_supported, icon: "🛠" },
              { label: "Snippets", value: stats.snippets_available + "+", icon: "✂" },
              { label: "Languages", value: stats.languages_supported, icon: "🌐" },
            ].map((s) => (
              <div key={s.label} className="cyber-card" style={{ textAlign: "center", padding: 20 }}>
                <div style={{ fontSize: "1.8rem" }}>{s.icon}</div>
                <div style={{ fontFamily: "var(--font-code)", fontSize: "1.6rem", fontWeight: 700, color: "var(--gold)", marginTop: 8 }}>{s.value}</div>
                <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-dim)", marginTop: 4 }}>{s.label}</div>
              </div>
            ))}
          </div>
          <div className="cyber-card" style={{ padding: 20 }}>
            <h3 style={{ marginBottom: 12, color: "var(--text-dim)", fontSize: "0.8rem", textTransform: "uppercase" }}>System Info</h3>
            <div style={{ fontFamily: "var(--font-code)", fontSize: "0.78rem", color: "var(--text)", lineHeight: 2, display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 16px" }}>
              <span style={{ color: "var(--text-dim)" }}>Engine:</span><span>LocalCodeGenerator v1</span>
              <span style={{ color: "var(--text-dim)" }}>Completion:</span><span>Prometheus CompletionEngine</span>
              <span style={{ color: "var(--text-dim)" }}>API:</span><span>FastAPI + WebSockets</span>
              <span style={{ color: "var(--text-dim)" }}>Storage:</span><span>~/.prometheus/</span>
              <span style={{ color: "var(--text-dim)" }}>External APIs:</span><span style={{ color: "#00c850" }}>None — 100% local</span>
            </div>
          </div>
        </div>
      )}

      {tab === "Generator" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
          <div className="cyber-card" style={{ padding: 20 }}>
            <h3 style={{ marginBottom: 14, fontSize: "0.8rem", textTransform: "uppercase", color: "var(--text-dim)" }}>Input</h3>
            <textarea
              className="cyber-input"
              rows={6}
              placeholder="Enter a prompt… e.g. 'CRUD API for users'"
              value={genPrompt}
              onChange={(e) => setGenPrompt(e.target.value)}
              style={{ resize: "none", marginBottom: 12 }}
            />
            <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
              <select className="cyber-input" style={{ width: 150 }} value={genLang} onChange={(e) => setGenLang(e.target.value)}>
                {["python", "javascript", "typescript", "go", "rust", "bash"].map((l) => <option key={l}>{l}</option>)}
              </select>
              <button className="cyber-btn primary" onClick={handleGenerate} disabled={genLoading}>{genLoading ? "Generating…" : "⚡ Generate"}</button>
            </div>
          </div>
          <div className="cyber-card" style={{ padding: 20 }}>
            <h3 style={{ marginBottom: 14, fontSize: "0.8rem", textTransform: "uppercase", color: "var(--text-dim)" }}>Output</h3>
            <pre style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 4, padding: 14, height: 220, overflow: "auto", fontFamily: "var(--font-code)", fontSize: "0.78rem", whiteSpace: "pre-wrap", wordBreak: "break-word", color: "#ccc" }}>
              {genResult || <span style={{ color: "var(--text-dim)" }}>Generated code will appear here…</span>}
            </pre>
          </div>
        </div>
      )}

      {tab === "Completion" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
          <div className="cyber-card" style={{ padding: 20 }}>
            <h3 style={{ marginBottom: 14, fontSize: "0.8rem", textTransform: "uppercase", color: "var(--text-dim)" }}>Code Input</h3>
            <textarea
              className="cyber-input"
              rows={8}
              placeholder="Enter code to complete…"
              value={complCode}
              onChange={(e) => setComplCode(e.target.value)}
              style={{ resize: "none", fontFamily: "var(--font-code)", fontSize: "0.78rem", marginBottom: 12 }}
            />
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <select className="cyber-input" style={{ width: 150 }} value={complLang} onChange={(e) => setComplLang(e.target.value)}>
                {["python", "javascript", "typescript", "go", "rust", "bash"].map((l) => <option key={l}>{l}</option>)}
              </select>
              <button className="cyber-btn primary" onClick={handleComplete} disabled={complLoading}>{complLoading ? "…" : "Complete"}</button>
            </div>
          </div>
          <div className="cyber-card" style={{ padding: 20 }}>
            <h3 style={{ marginBottom: 14, fontSize: "0.8rem", textTransform: "uppercase", color: "var(--text-dim)" }}>Completions</h3>
            {completions.length === 0 ? (
              <p style={{ color: "var(--text-dim)", fontSize: "0.8rem" }}>No completions yet.</p>
            ) : (
              <div style={{ overflowY: "auto", maxHeight: 280 }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.78rem" }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--border)" }}>
                      {["Label", "Kind", "Detail"].map((h) => <th key={h} style={{ textAlign: "left", padding: "4px 8px", color: "var(--text-dim)", fontWeight: 600 }}>{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {completions.map((c, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid rgba(255,0,51,0.1)" }}>
                        <td style={{ padding: "5px 8px", fontFamily: "var(--font-code)", color: "var(--red-bright)" }}>{c.label}</td>
                        <td style={{ padding: "5px 8px", color: "var(--gold)" }}>{c.kind}</td>
                        <td style={{ padding: "5px 8px", color: "var(--text-dim)" }}>{c.detail}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "Packages" && (
        <div className="cyber-card" style={{ padding: 24 }}>
          <h3 style={{ marginBottom: 16, fontSize: "0.8rem", textTransform: "uppercase", color: "var(--text-dim)" }}>Install Packages</h3>
          <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
            <input className="cyber-input" placeholder="Package names (space/comma separated)…" value={pkgInput} onChange={(e) => setPkgInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleInstallPkg()} />
            <button className="cyber-btn primary" onClick={handleInstallPkg}>Install</button>
          </div>
          {pkgOutput && (
            <pre style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 4, padding: 14, fontFamily: "var(--font-code)", fontSize: "0.78rem", whiteSpace: "pre-wrap", color: "#ccc", maxHeight: 300, overflow: "auto" }}>
              {pkgOutput}
            </pre>
          )}
        </div>
      )}

      {tab === "Terminal" && (
        <div className="cyber-card" style={{ padding: 20 }}>
          <div style={{ display: "flex", gap: 10, marginBottom: 16, alignItems: "center", flexWrap: "wrap" }}>
            <label style={{ fontSize: "0.75rem", color: "var(--text-dim)", whiteSpace: "nowrap" }}>Project:</label>
            <select className="cyber-input" style={{ maxWidth: 300 }} value={termProjectId} onChange={(e) => setTermProjectId(e.target.value)}>
              <option value="">-- Select project --</option>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          <Terminal output={termOutput} onCommand={handleTermCmd} height={400} title="SYSTEM TERMINAL" />
        </div>
      )}

      {tab === "Settings" && (
        <div className="cyber-card" style={{ padding: 24 }}>
          <h3 style={{ marginBottom: 20, fontSize: "0.8rem", textTransform: "uppercase", color: "var(--text-dim)" }}>Android + Editor Preferences</h3>
          <div style={{ display: "grid", gap: 18, maxWidth: 520 }}>
            <div>
              <label style={{ display: "block", fontSize: "0.7rem", textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 6 }}>Backend URL</label>
              <input
                className="cyber-input"
                value={apiBaseInput}
                onChange={(e) => setApiBaseInput(e.target.value)}
                placeholder="https://your-server.example.com:8000"
              />
              <p style={{ marginTop: 8, fontSize: "0.74rem", color: "var(--text-dim)" }}>
                {isNativeShell()
                  ? "Required on Android so the APK can reach your FastAPI backend over the network."
                  : "Optional in the browser. Leave empty to keep using the current site's /api and /ws routes."}
              </p>
            </div>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <button className="cyber-btn primary" onClick={handleSaveSettings}>Save Settings</button>
              <button className="cyber-btn" onClick={handleCheckBackend}>Test Backend</button>
            </div>
            {settingsNotice && <p style={{ fontSize: "0.76rem", color: "var(--gold)" }}>{settingsNotice}</p>}
            {backendCheck.message && (
              <p style={{ fontSize: "0.76rem", color: backendCheck.status === "ok" ? "#00c850" : backendCheck.status === "checking" ? "var(--gold)" : "var(--red-bright)" }}>
                {backendCheck.message}
              </p>
            )}
            <div>
              <label style={{ display: "block", fontSize: "0.7rem", textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 6 }}>Font Size</label>
              <input type="range" min={10} max={20} value={editorSettings.fontSize} onChange={(e) => setEditorSettings({ ...editorSettings, fontSize: +e.target.value })} style={{ width: "100%" }} />
              <span style={{ fontSize: "0.75rem", color: "var(--gold)" }}>{editorSettings.fontSize}px</span>
            </div>
            <div>
              <label style={{ display: "flex", gap: 10, alignItems: "center", cursor: "pointer", fontSize: "0.8rem" }}>
                <input type="checkbox" checked={editorSettings.minimap} onChange={(e) => setEditorSettings({ ...editorSettings, minimap: e.target.checked })} />
                Show Minimap
              </label>
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.7rem", textTransform: "uppercase", color: "var(--text-dim)", marginBottom: 6 }}>Word Wrap</label>
              <select className="cyber-input" value={editorSettings.wordWrap} onChange={(e) => setEditorSettings({ ...editorSettings, wordWrap: e.target.value })}>
                <option value="on">On</option>
                <option value="off">Off</option>
                <option value="wordWrapColumn">Column</option>
              </select>
            </div>
          </div>
          <p style={{ marginTop: 20, fontSize: "0.75rem", color: "var(--text-dim)" }}>
            Saved editor settings apply to the Builder immediately the next time it gains focus.
          </p>
        </div>
      )}
    </div>
  );
}
