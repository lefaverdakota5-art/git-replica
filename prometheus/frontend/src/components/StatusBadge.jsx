import React from "react";

export default function StatusBadge({ status = "idle" }) {
  return (
    <span className={`cyber-badge ${status}`}>
      <span className="dot" />
      {status}
    </span>
  );
}
