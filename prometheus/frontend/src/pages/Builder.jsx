import React, { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Editor from "@monaco-editor/react";
import api from "../api";
import FileTree from "../components/FileTree";
import StatusBadge from "../components/StatusBadge";
import Terminal from "../components/Terminal";
import { getEditorSettings, getWsUrl, needsBackendConfiguration } from "../config";

const EXT_LANG = {
  py: "python", js: "javascript", jsx: "javascript", ts: "typescript", tsx: "typescript",
  json: "json", html: "html", css: "css", md: "markdown", yml: "yaml", yaml: "yaml",
  go: "go", rs: "rust", sh: "shell", txt: "plaintext",
};

const MOBILE_BREAKPOINT = 960;

function getLang(filename = "") {
  const ext = filename.split(".").pop().toLowerCase();
  return EXT_LANG[ext] || "plaintext";
}

export default function Builder() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [fileTree, setFileTree] = useState([]);
  const [openFiles, setOpenFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);
  const [fileContent, setFileContent] = useState("");
  const [unsaved, setUnsaved] = useState(false);
  const [termOutput, setTermOutput] = useState("");
  const [termOpen, setTermOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { role: "ai", content: "Hello! I'm your AI assistant. Describe what you'd like to build or modify." },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [wsStatus, setWsStatus] = useState("disconnected");
  const [genStatus, setGenStatus] = useState("");
  const [view, setView] = useState("code");
  const [editorSettings, setEditorSettings] = useState(() => getEditorSettings());
  const [isMobile, setIsMobile] = useState(() => typeof window !== "undefined" && window.innerWidth < MOBILE_BREAKPOINT);
  const [mobilePanel, setMobilePanel] = useState("editor");
  const wsRef = useRef(null);
  const chatBottomRef = useRef(null);
  const backendNeedsSetup = needsBackendConfiguration();

  const loadProject = useCallback(() => {
    api.getProject(projectId).then(setProject).catch(() => navigate("/projects"));
    api.listFiles(projectId).then((r) => setFileTree(r.tree || [])).catch(() => {});
  }, [projectId, navigate]);

  useEffect(() => { loadProject(); }, [loadProject]);

  useEffect(() => {
    const syncEditorSettings = () => setEditorSettings(getEditorSettings());
    const syncViewport = () => setIsMobile(window.innerWidth < MOBILE_BREAKPOINT);
    window.addEventListener("focus", syncEditorSettings);
    window.addEventListener("storage", syncEditorSettings);
    window.addEventListener("resize", syncViewport);
    return () => {
      window.removeEventListener("focus", syncEditorSettings);
      window.removeEventListener("storage", syncEditorSettings);
      window.removeEventListener("resize", syncViewport);
    };
  }, []);

  useEffect(() => {
    if (!isMobile) setMobilePanel("editor");
  }, [isMobile]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  useEffect(() => {
    const wsUrl = getWsUrl("/ws/generate");
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setWsStatus("connected");
    ws.onclose = () => setWsStatus("disconnected");
    ws.onerror = () => setWsStatus("error");
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "chunk") {
          setChatMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last && last.role === "ai" && last.streaming) {
              return [...prev.slice(0, -1), { ...last, content: last.content + msg.content }];
            }
            return [...prev, { role: "ai", content: msg.content, streaming: true }];
          });
        } else if (msg.type === "done") {
          setChatMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last && last.streaming) {
              return [...prev.slice(0, -1), { role: "ai", content: last.content, streaming: false }];
            }
            return prev;
          });
          setGenStatus(`Generated ${msg.saved_files?.length || 0} files`);
          if (msg.saved_files?.length) loadProject();
        } else if (msg.status === "generating") {
          setGenStatus(msg.message);
        } else if (msg.error) {
          setChatMessages((prev) => [...prev, { role: "ai", content: `Error: ${msg.error}` }]);
        }
      } catch (_) {}
    };
    return () => { ws.close(); };
  }, [projectId, loadProject]);

  const handleSendChat = () => {
    if (!chatInput.trim()) return;
    const msg = chatInput.trim();
    setChatMessages((prev) => [...prev, { role: "user", content: msg }]);
    setChatInput("");
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ prompt: msg, language: "python", project_id: projectId }));
    } else {
      api.generate(msg, "python", projectId).then((r) => {
        setChatMessages((prev) => [...prev, { role: "ai", content: "```\n" + r.code + "\n```" }]);
        loadProject();
      }).catch((e) => {
        setChatMessages((prev) => [...prev, { role: "ai", content: "Error: " + e.message }]);
      });
    }
  };

  const handleSelectFile = async (node) => {
    if (unsaved && activeFile) {
      if (!window.confirm("You have unsaved changes. Discard?")) return;
      setUnsaved(false);
    }
    setActiveFile(node.path);
    if (!openFiles.find((f) => f.path === node.path)) {
      setOpenFiles((prev) => [...prev, node]);
    }
    const r = await api.readFile(projectId, node.path).catch(() => null);
    if (r) {
      setFileContent(r.content);
      if (isMobile) setMobilePanel("editor");
    }
  };

  const handleSave = async () => {
    if (!activeFile) return;
    await api.updateFile(projectId, activeFile, fileContent).catch((e) => alert(e.message));
    setUnsaved(false);
  };

  const handleAddFile = async () => {
    const name = window.prompt("File name (e.g. utils.py):");
    if (!name) return;
    await api.createFile(projectId, name, "").catch((e) => alert(e.message));
    loadProject();
  };

  const handleDeleteFile = async (path) => {
    if (!window.confirm("Delete " + path + "?")) return;
    await api.deleteFile(projectId, path).catch((e) => alert(e.message));
    setOpenFiles((prev) => prev.filter((f) => f.path !== path));
    if (activeFile === path) {
      setActiveFile(null);
      setFileContent("");
    }
    loadProject();
  };

  const handleRun = async () => {
    setTermOpen(true);
    if (isMobile) setMobilePanel("terminal");
    setTermOutput("Running…\n");
    try {
      const r = await api.runProject(projectId);
      setTermOutput(r.output || "(no output)");
      loadProject();
    } catch (e) {
      setTermOutput("Error: " + e.message);
    }
  };

  const handleExec = async (cmd) => {
    try {
      const r = await api.execCommand(projectId, cmd);
      setTermOutput((prev) => prev + `$ ${cmd}\n${r.output}\n`);
    } catch (e) {
      setTermOutput((prev) => prev + `Error: ${e.message}\n`);
    }
  };

  const handleDeploy = async () => {
    try {
      const r = await api.createDeploy(projectId);
      setTermOutput("Deploy files created:\n" + r.files_created.join("\n"));
      setTermOpen(true);
      if (isMobile) setMobilePanel("terminal");
      loadProject();
    } catch (e) {
      alert("Deploy error: " + e.message);
    }
  };

  const currentLang = activeFile ? getLang(activeFile) : "plaintext";
  const mobileTabs = [
    { id: "chat", label: "Chat" },
    { id: "files", label: "Files" },
    { id: "editor", label: "Editor" },
    { id: "terminal", label: "Terminal" },
  ];

  const renderChatPanel = () => (
    <div style={{ width: isMobile ? "100%" : 300, borderRight: isMobile ? "none" : "1px solid var(--border)", borderBottom: isMobile ? "1px solid var(--border)" : "none", display: "flex", flexDirection: "column", background: "var(--surface-1)", flexShrink: 0, minHeight: isMobile ? 320 : 0 }}>
      <div className="cyber-panel-header">💬 AI CHAT</div>
      <div style={{ flex: 1, overflowY: "auto", padding: 12, display: "flex", flexDirection: "column", gap: 10, maxHeight: isMobile ? "45vh" : "none" }}>
        {chatMessages.map((msg, i) => (
          <div
            key={i}
            style={{
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "88%",
              background: msg.role === "user" ? "rgba(255,0,51,0.15)" : "var(--surface-2)",
              border: `1px solid ${msg.role === "user" ? "rgba(255,0,51,0.3)" : "var(--border)"}`,
              borderRadius: 8,
              padding: "8px 12px",
              fontSize: "0.78rem",
              lineHeight: 1.55,
              fontFamily: msg.content.includes("```") ? "var(--font-code)" : "var(--font-ui)",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {msg.streaming ? msg.content + "▊" : msg.content}
          </div>
        ))}
        <div ref={chatBottomRef} />
      </div>
      <div style={{ borderTop: "1px solid var(--border)", padding: 10, display: "flex", gap: 8 }}>
        <input
          className="cyber-input"
          style={{ flex: 1, fontSize: "0.78rem", padding: "8px 10px" }}
          placeholder="Ask AI…"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSendChat();
            }
          }}
        />
        <button className="cyber-btn primary" style={{ padding: "8px 12px" }} onClick={handleSendChat}>→</button>
      </div>
    </div>
  );

  const renderFilesPanel = () => (
    <div style={{ width: isMobile ? "100%" : 220, borderRight: isMobile ? "none" : "1px solid var(--border)", borderBottom: isMobile ? "1px solid var(--border)" : "none", background: "var(--surface-1)", flexShrink: 0, display: "flex", flexDirection: "column", minHeight: isMobile ? 320 : 0 }}>
      <div className="cyber-panel-header">📁 FILES</div>
      <div style={{ flex: 1, overflow: "auto", maxHeight: isMobile ? "55vh" : "none" }}>
        <FileTree tree={fileTree} activeFile={activeFile} onSelect={handleSelectFile} onDelete={handleDeleteFile} onAddFile={handleAddFile} />
      </div>
    </div>
  );

  const renderTerminalPanel = (height = 170) => (
    <Terminal output={termOutput} onCommand={handleExec} height={height} title={isMobile ? "PROJECT TERMINAL" : ""} />
  );

  const renderEditorPanel = () => (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", minHeight: isMobile ? 420 : 0 }}>
      <div style={{ background: "var(--surface-2)", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", padding: "0 8px", minHeight: 36, gap: 4, overflowX: "auto", flexShrink: 0, flexWrap: isMobile ? "wrap" : "nowrap" }}>
        {openFiles.map((f) => (
          <button
            key={f.path}
            onClick={() => handleSelectFile(f)}
            style={{
              background: activeFile === f.path ? "var(--surface-3)" : "transparent",
              border: activeFile === f.path ? "1px solid var(--border)" : "1px solid transparent",
              borderRadius: "4px 4px 0 0",
              color: activeFile === f.path ? "var(--red-bright)" : "var(--text-dim)",
              padding: "4px 12px",
              fontSize: "0.75rem",
              cursor: "pointer",
              fontFamily: "var(--font-code)",
              whiteSpace: "nowrap",
            }}
          >
            {f.name}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <div style={{ display: "flex", gap: 6, marginRight: 4, padding: isMobile ? "4px 0" : 0 }}>
          {["code", "preview"].map((v) => (
            <button key={v} className="cyber-btn" style={{ padding: "3px 10px", fontSize: "0.68rem", ...(view === v ? { borderColor: "var(--gold)", color: "var(--gold)" } : {}) }} onClick={() => setView(v)}>
              {v === "code" ? "⌨ Code" : "👁 Preview"}
            </button>
          ))}
          <button className="cyber-btn" style={{ padding: "3px 10px", fontSize: "0.68rem" }} onClick={handleSave} disabled={!unsaved}>
            {unsaved ? "💾 Save" : "✓ Saved"}
          </button>
        </div>
      </div>

      <div style={{ flex: 1, overflow: "hidden", position: "relative", minHeight: isMobile ? "55vh" : 0 }}>
        {view === "code" ? (
          activeFile ? (
            <Editor
              height={isMobile ? "55vh" : "100%"}
              language={currentLang}
              value={fileContent}
              theme="vs-dark"
              onChange={(v) => { setFileContent(v || ""); setUnsaved(true); }}
              options={{
                fontSize: editorSettings.fontSize,
                fontFamily: "JetBrains Mono, Fira Code, monospace",
                minimap: { enabled: editorSettings.minimap },
                scrollBeyondLastLine: false,
                wordWrap: editorSettings.wordWrap,
                padding: { top: 12 },
                automaticLayout: true,
              }}
              onMount={(editor) => {
                editor.addCommand(2097, handleSave);
              }}
            />
          ) : (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--text-dim)", flexDirection: "column", gap: 12 }}>
              <span style={{ fontSize: "2.5rem" }}>📄</span>
              <span>Select a file to edit</span>
            </div>
          )
        ) : (
          <iframe
            srcDoc={currentLang === "html" ? fileContent : `<pre style="color:#f0f0f0;background:#0a0a0a;padding:20px;font-family:monospace;white-space:pre-wrap;">${fileContent.replace(/</g, "&lt;")}</pre>`}
            style={{ width: "100%", height: isMobile ? "55vh" : "100%", border: "none", background: "#fff" }}
            sandbox="allow-scripts"
            title="Preview"
          />
        )}
      </div>

      {!isMobile && (
        <div style={{ borderTop: "1px solid var(--border)", height: termOpen ? 200 : 30, transition: "height 0.2s", flexShrink: 0 }}>
          <div
            style={{
              background: "var(--surface-2)",
              padding: "4px 12px",
              fontSize: "0.7rem",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "var(--text-dim)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 8,
              borderBottom: termOpen ? "1px solid var(--border)" : "none",
            }}
            onClick={() => setTermOpen(!termOpen)}
          >
            <span style={{ color: "var(--red-bright)" }}>▶</span>
            TERMINAL
            <span style={{ marginLeft: "auto" }}>{termOpen ? "▾" : "▸"}</span>
          </div>
          {termOpen && renderTerminalPanel()}
        </div>
      )}
    </div>
  );

  return (
    <div style={{ minHeight: "calc(100vh - 52px)", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <div style={{ background: "var(--surface-2)", borderBottom: "1px solid var(--border)", padding: "8px 16px", minHeight: 44, display: "flex", alignItems: "center", gap: 12, flexShrink: 0, flexWrap: "wrap" }}>
        <span style={{ fontFamily: "var(--font-code)", fontWeight: 700, fontSize: "0.9rem" }}>{project?.name || "…"}</span>
        <StatusBadge status={project?.status || "stopped"} />
        <span style={{ color: "var(--text-dim)", fontSize: "0.75rem" }}>{project?.framework}</span>
        <div style={{ flex: 1 }} />
        {genStatus && <span style={{ fontSize: "0.72rem", color: "var(--gold)" }}>{genStatus}</span>}
        <span style={{ fontSize: "0.65rem", color: wsStatus === "connected" ? "#00c850" : "var(--red-bright)" }}>{wsStatus === "connected" ? "● WS" : "○ WS"}</span>
        <button className="cyber-btn" onClick={handleRun}>▶ Run</button>
        <button className="cyber-btn gold" onClick={handleDeploy}>🚀 Deploy</button>
      </div>

      {backendNeedsSetup && (
        <div style={{ borderBottom: "1px solid rgba(255,215,0,0.35)", background: "rgba(255,215,0,0.08)", color: "var(--gold)", padding: "10px 16px", fontSize: "0.8rem" }}>
          Set your backend URL in System Control → Settings before using this Android build.
        </div>
      )}

      {isMobile && (
        <div style={{ display: "flex", gap: 8, padding: 10, borderBottom: "1px solid var(--border)", overflowX: "auto", background: "var(--surface-1)" }}>
          {mobileTabs.map((tab) => (
            <button
              key={tab.id}
              className="cyber-btn"
              style={{ padding: "6px 12px", fontSize: "0.72rem", whiteSpace: "nowrap", ...(mobilePanel === tab.id ? { borderColor: "var(--gold)", color: "var(--gold)" } : {}) }}
              onClick={() => setMobilePanel(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      )}

      <div style={{ flex: 1, display: "flex", flexDirection: isMobile ? "column" : "row", overflow: "hidden" }}>
        {!isMobile && renderChatPanel()}
        {!isMobile && renderFilesPanel()}
        {!isMobile && renderEditorPanel()}
        {isMobile && mobilePanel === "chat" && renderChatPanel()}
        {isMobile && mobilePanel === "files" && renderFilesPanel()}
        {isMobile && mobilePanel === "editor" && renderEditorPanel()}
        {isMobile && mobilePanel === "terminal" && (
          <div style={{ padding: 12, background: "var(--surface-1)", flex: 1 }}>
            {renderTerminalPanel(420)}
          </div>
        )}
      </div>
    </div>
  );
}
