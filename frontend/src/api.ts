import axios from "axios";

const BACKEND = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

export async function listRuns() {
  const res = await axios.get(`${BACKEND}/runs`);
  return res.data.runs;
}

export async function triggerRun() {
  const res = await axios.post(`${BACKEND}/run`);
  return res.data;
}

export function tileURL(z: number, x:number, y:number, run?: string) {
  let url = `${BACKEND}/tile/${z}/${x}/${y}.png`;
  if (run) url += `?run=${run}`;
  return url;
}

