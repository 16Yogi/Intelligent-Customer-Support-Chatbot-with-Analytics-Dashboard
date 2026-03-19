/**
 * Backend API base URL.
 * - Dev: leave VITE_API_URL unset → uses http://localhost:8000
 * - Production: set VITE_API_URL to your backend URL, or set to "" for same-origin /api (nginx proxy)
 */
const env = import.meta.env.VITE_API_URL as string | undefined;
export const API_BASE =
  env !== undefined ? (env.trim() || "") : "http://localhost:8000";
