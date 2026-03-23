import React, { useState, useRef } from "react";

function TreeNode({ node, activeFile, onSelect, onDelete, depth = 0 }) {
  const [open, setOpen] = useState(depth < 2);
  const [ctxMenu, setCtxMenu] = useState(null);
  const isDir = node.type === "directory";

  const handleContextMenu = (e) => {
    e.preventDefault();
    setCtxMenu({ x: e.clientX, y: e.clientY });
  };

  const closeCtx = () => setCtxMenu(null);

  return (
    <div>
      <div
        className={`tree-node${activeFile === node.path ? " active" : ""}`}
        style={{ paddingLeft: depth * 14 + 8 }}
        onClick={() => {
          if (isDir) setOpen(!open);
          else onSelect(node);
        }}
        onContextMenu={handleContextMenu}
      >
        <span className="tree-icon">{isDir ? (open ? "📂" : "📁") : "📄"}</span>
        <span className="tree-name">{node.name}</span>
      </div>
      {ctxMenu && (
        <>
          <div style={{ position: "fixed", inset: 0, zIndex: 999 }} onClick={closeCtx} />
          <div style={{
            position: "fixed",
            left: ctxMenu.x,
            top: ctxMenu.y,
            background: "var(--surface-2)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius)",
            zIndex: 1000,
            overflow: "hidden",
            minWidth: 140,
          }}>
            {!isDir && (
              <button
                style={{ display: "block", width: "100%", padding: "8px 14px", background: "none", border: "none", color: "var(--red-bright)", cursor: "pointer", textAlign: "left", fontSize: "0.8rem" }}
                onClick={() => { onDelete && onDelete(node.path); closeCtx(); }}
              >
                🗑 Delete
              </button>
            )}
            <button
              style={{ display: "block", width: "100%", padding: "8px 14px", background: "none", border: "none", color: "var(--text)", cursor: "pointer", textAlign: "left", fontSize: "0.8rem" }}
              onClick={closeCtx}
            >
              ✕ Close
            </button>
          </div>
        </>
      )}
      {isDir && open && node.children && node.children.map((child, i) => (
        <TreeNode key={i} node={child} activeFile={activeFile} onSelect={onSelect} onDelete={onDelete} depth={depth + 1} />
      ))}
      <style>{`
        .tree-node {
          display: flex;
          align-items: center;
          gap: 6px;
          padding-top: 4px;
          padding-bottom: 4px;
          cursor: pointer;
          border-radius: 4px;
          font-size: 0.82rem;
          color: var(--text-dim);
          transition: background 0.15s;
          user-select: none;
        }
        .tree-node:hover { background: var(--surface-2); color: var(--text); }
        .tree-node.active { background: rgba(255,0,51,0.15); color: var(--red-bright); }
        .tree-icon { font-size: 0.9em; }
        .tree-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      `}</style>
    </div>
  );
}

export default function FileTree({ tree = [], activeFile, onSelect, onDelete, onAddFile }) {
  return (
    <div style={{ height: "100%", overflowY: "auto", padding: "8px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8, padding: "0 4px" }}>
        <span style={{ fontSize: "0.7rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-dim)" }}>Files</span>
        {onAddFile && (
          <button
            onClick={onAddFile}
            style={{ background: "none", border: "none", color: "var(--red-bright)", cursor: "pointer", fontSize: "1rem", lineHeight: 1 }}
            title="New file"
          >+</button>
        )}
      </div>
      {tree.length === 0 ? (
        <div style={{ color: "var(--text-dim)", fontSize: "0.78rem", padding: "8px 4px" }}>No files yet.</div>
      ) : tree.map((node, i) => (
        <TreeNode key={i} node={node} activeFile={activeFile} onSelect={onSelect} onDelete={onDelete} depth={0} />
      ))}
    </div>
  );
}
