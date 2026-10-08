import { defaultAllowedOrigins, defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true, // Prevents Vite "403 Blocked Host" errors when accessed via *.trycloudflare.com or custom tunnel domains
  }
})
