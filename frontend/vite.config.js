import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Dev: /api -> backend (8000). Prod: FastAPI frontend/dist ni o'zi beradi.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173, proxy: { "/api": process.env.VITE_BACKEND || "http://localhost:8000" } },
});
