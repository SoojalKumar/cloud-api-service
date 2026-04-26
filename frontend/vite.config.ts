import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// API proxy avoids CORS in local dev — frontend on :5173 calls /api/* and Vite
// forwards to the FastAPI backend on :8000 with the Origin rewritten.
const BACKEND_URL = process.env.VITE_BACKEND_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: BACKEND_URL,
        changeOrigin: true,
      },
    },
  },
});
