import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import fs from 'fs';

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
})
