import { defineConfig } from 'vite';

export default defineConfig({
  base: './', // Relative base for 100% free hosting on GitHub Pages, Vercel, Netlify, Render
  server: {
    port: 3000,
    host: true
  }
});
