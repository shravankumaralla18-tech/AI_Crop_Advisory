import { BACKEND_ORIGIN } from "./constants";

export const formatDate = (iso) =>
  new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });

export const formatPrice = (value, currency = "INR") =>
  new Intl.NumberFormat(undefined, { style: "currency", currency, maximumFractionDigits: 0 }).format(value);

export const percent = (value) => `${(value * 100).toFixed(1)}%`;

export const imageSrc = (url) => (url?.startsWith("http") ? url : `${BACKEND_ORIGIN}${url}`);

// FastAPI returns {detail: string} or {detail: [{msg}]}
export function errorMessage(error, fallback = "Something went wrong. Try again.") {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail.map((d) => d.msg).join(". ");
  if (!error?.response && (error?.request || error?.message === "Network Error")) {
    return "Cannot reach the server. Check your connection and that the backend is running.";
  }
  if (error?.response) return `The server returned HTTP ${error.response.status}. Please try again.`;

  return fallback;
}
