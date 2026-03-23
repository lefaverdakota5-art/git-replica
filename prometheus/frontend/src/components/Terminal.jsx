import React, { useRef, useEffect, useState } from "react";

export default function Terminal({ output = "", onCommand, height = 200, title = "TERMINAL" }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [output]);

  const handleKey = (e) => {
    if (e.key === "Enter" && onCommand && input.trim()) {
      onCommand(input.trim());
      setInput("");
    }
  };

  return (
    <div style={{
      background: "#050505",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius)",
      height,
      display: "flex",
      flexDirection: "column",
      overflow: "hidden",
    }}>
      <div style={{
        background: "var(--surface-2)",
        borderBottom: "1px solid var(--border)",
        padding: "4px 12px",
        fontSize: "0.7rem",
        fontWeight: 700,
        textTransform: "uppercase",
        letterSpacing: "0.1em",
        color: "var(--text-dim)",
        display: "flex",
        alignItems: "center",
        gap: 8,
      }}>
        <span style={{ color: "var(--red-bright)" }}>▶</span>
        {title}
      </div>
      <div style={{
        flex: 1,
        overflowY: "auto",
        padding: "10px 14px",
        fontFamily: "var(--font-code)",
        fontSize: "0.78rem",
        lineHeight: 1.6,
        whiteSpace: "pre-wrap",
        wordBreak: "break-all",
        color: "#ccc",
      }}>
        {output || <span style={{ color: "var(--text-dim)" }}>No output yet…</span>}
        <div ref={bottomRef} />
      </div>
      {onCommand && (
        <div style={{
          borderTop: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          padding: "0 12px",
          gap: 8,
        }}>
          <span style={{ color: "var(--red-bright)", fontFamily: "var(--font-code)", fontSize: "0.8rem" }}>$</span>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Enter command…"
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              color: "var(--text)",
              fontFamily: "var(--font-code)",
              fontSize: "0.78rem",
              padding: "8px 0",
            }}
          />
        </div>
      )}
    </div>
  );
}
