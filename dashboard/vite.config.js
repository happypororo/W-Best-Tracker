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
      '3000-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai',
      '3001-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai',
      '3002-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai',
      '3003-iner9p11l1qajaf54x3x7-5634da27.sandbox.novita.ai'
    ]
  }
})
