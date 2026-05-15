import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import vercel from "@astrojs/vercel";

export default defineConfig({
  site: "https://{{DOMAIN}}",
  integrations: [sitemap()],
  vite: {
    plugins: [tailwindcss()],
  },
  output: "static",
  adapter: vercel(),
});
