const defaultApiUrl = import.meta.env.PROD
  ? "https://ai-crop-advisory-zjgp.onrender.com/api"
  : "http://localhost:8000/api";

function resolveApiUrl() {
  const envUrl = import.meta.env.VITE_API_URL?.trim();
  const raw = envUrl || defaultApiUrl;
  const stripped = raw.replace(/\/+$/, "");
  return stripped.endsWith("/api") ? stripped : `${stripped}/api`;
}

export const API_URL = resolveApiUrl();
// Uploaded leaf photos are served from the backend root, not /api
export const BACKEND_ORIGIN = API_URL.replace(/\/api\/?$/, "");
export const TOKEN_KEY = "crop_advisory_token";

export const SIGNAL_LABELS = { sell: "Sell", hold: "Hold", monitor: "Watch" };
