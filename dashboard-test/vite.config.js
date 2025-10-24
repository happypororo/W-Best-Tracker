import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: false,
    allowedHosts: [
      '3000-is73bj77dclhgdm3vfpjp-2e77fc33.sandbox.novita.ai',
      '3001-is73bj77dclhgdm3vfpjp-2e77fc33.sandbox.novita.ai',
      '3002-is73bj77dclhgdm3vfpjp-2e77fc33.sandbox.novita.ai',
      '3003-is73bj77dclhgdm3vfpjp-2e77fc33.sandbox.novita.ai',
      '.sandbox.novita.ai'
    ]
  }
})
