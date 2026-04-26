import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// API proxy avoids CORS in local dev — frontend on :5173 calls these paths
// and Vite forwards to the FastAPI backend on :8000 with Origin rewritten.
// /api/* covers task endpoints; /docs and /openapi.json keep the footer
// "OpenAPI / Swagger" link working out of the box.
const BACKEND_URL = process.env.VITE_BACKEND_URL ?? "http://localhost:8000";
const PROXY_TARGET = { target: BACKEND_URL, changeOrigin: true };

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": PROXY_TARGET,
      "/docs": PROXY_TARGET,
      "/openapi.json": PROXY_TARGET,
    },
  },
});
