import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import config from './src/config/config.js';

export default defineConfig(() => ({
  plugins: [vue(), tailwindcss()],
  server: {
    port: config.VITE_FRONTEND_PORT|| 5173,
  },
}));
