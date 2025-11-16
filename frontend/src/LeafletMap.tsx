import React, { useEffect, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { listRuns, tileURL, triggerRun } from "./api";

export default function LeafletMap() {
  const [map, setMap] = useState<L.Map | null>(null);
  const [runs, setRuns] = useState<string[]>([]);
  const [selectedRun, setSelectedRun] = useState<string | undefined>(undefined);
  const [classificationLayer, setClassificationLayer] = useState<L.TileLayer | null>(null);
  const [opacity, setOpacity] = useState<number>(0.7);

  useEffect(() => {
    const mapEl = L.map("map", {
      center: [-14.3, 137.4],
      zoom: 12
    });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19
    }).addTo(mapEl);

    setMap(mapEl);
    // Add placeholder property polygon
    const poly = L.polygon([
      [-14.2, 137.3],
      [-14.2, 137.5],
      [-14.4, 137.5],
      [-14.4, 137.3]
    ], {color: "yellow", weight:2}).addTo(mapEl);
    poly.bindPopup("Lorella Springs (approx)");
  }, []);

  useEffect(() => {
    // fetch runs list
    listRuns().then(r => {
      setRuns(r);
      if (r.length > 0) setSelectedRun(r[0]);
    });
  }, []);

  useEffect(() => {
    if (!map) return;
    // remove existing classification layer
    if (classificationLayer) {
      map.removeLayer(classificationLayer);
      setClassificationLayer(null);
    }
    if (!selectedRun) return;
    const tileUrl = (z:number, x:number, y:number) => tileURL(z,x,y,selectedRun);
    const layer = L.tileLayer(tileUrl("{z}","{x}","{y}"), {
      tileSize: 256,
      opacity: opacity,
      maxZoom: 19,
      attribution: "Classification overlay"
    });
    layer.addTo(map);
    setClassificationLayer(layer);
    return () => { layer.remove(); };
  }, [selectedRun, map, opacity]);

  const handleRunNow = async () => {
    await triggerRun();
    const r = await listRuns();
    setRuns(r);
    if (r.length > 0) setSelectedRun(r[0]);
  };

  return (
    <div style={{ height: "100%", display: "flex" }}>
      <div id="map" style={{ flex: 1 }} />
      <div style={{ width: 320, padding: 12, background: "#f7f7f7" }}>
        <h3>Controls</h3>
        <button onClick={handleRunNow}>Run demo pipeline now</button>
        <div style={{ marginTop: 12 }}>
          <label>Historical runs</label>
          <select value={selectedRun} onChange={e => setSelectedRun(e.target.value)} style={{ width: "100%" }}>
            {runs.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <div style={{ marginTop: 12 }}>
          <label>Overlay opacity: {Math.round(opacity*100)}%</label>
          <input type="range" min={0} max={1} step={0.05} value={opacity} onChange={e => setOpacity(Number(e.target.value))} />
        </div>
        <div style={{ marginTop: 12 }}>
          <h4>Legend</h4>
          <ul>
            <li><span style={{background:"#3CB44B",display:"inline-block",width:16,height:12}}/> Good grazing</li>
            <li><span style={{background:"#F0B239",display:"inline-block",width:16,height:12}}/> Moderate</li>
            <li><span style={{background:"#B43232",display:"inline-block",width:16,height:12}}/> Poor</li>
            <li><span style={{background:"#C8C8C8",display:"inline-block",width:16,height:12}}/> Cloud/No data</li>
          </ul>
        </div>
        <div style={{ marginTop: 12 }}>
          <small>Click on the map to see attributes (demo limited).</small>
        </div>
      </div>
    </div>
  );
}

