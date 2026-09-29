import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  server: {
    // Listen on all interfaces so other machines on the LAN can play.
    host: true,
    port: 5173,
    // Native file events were being missed on this Windows setup, leaving the dev
    // server serving stale modules; polling is slower but reliable.
    watch: { usePolling: true, interval: 200 },
  },
});
