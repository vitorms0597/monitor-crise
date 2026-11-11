// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// SITE_URL = origem (https://usuario.github.io); BASE_PATH = subpasta (/monitor-crise). Domínio próprio: BASE_PATH vazio.
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://vitorms0597.github.io',
  base: process.env.BASE_PATH ?? '/monitor-crise',
  trailingSlash: 'always',
  integrations: [sitemap()],
  build: { inlineStylesheets: 'auto' },
});
