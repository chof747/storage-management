// src/api/endpoint.tsx

const host = import.meta.env.VITE_API_ENDPOINT_HOST || "localhost";
const port = import.meta.env.VITE_API_ENDPOINT_PORT || "8000";

export const API_BASE = `http://${host}:${port}/api`;