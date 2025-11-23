import React from "react";
import LeafletMap from "./LeafletMap.tsx";

export default function App() {
  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <header style={{ padding: "8px", background: "#0b5cff", color: "white" }}>
        <h2>Grazing Mapper — Lorella Springs (Demo)</h2>
      </header>
      <div style={{ flex: 1 }}>
        <LeafletMap />
      </div>
    </div>
  );
}

