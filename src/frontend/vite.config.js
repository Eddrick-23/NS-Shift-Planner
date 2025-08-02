import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig(({mode}) => {

  const env = loadEnv(mode,process.cwd(),'');
  return {
    base: env.VITE_BASE_URL,
    plugins: [vue(), tailwindcss()],
    server: {
      port: env.VITE_FRONTEND_PORT|| 5173,
    },
  };
});
