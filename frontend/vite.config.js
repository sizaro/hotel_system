import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import {VitePWA} from 'vite-plugin-pwa';
export default defineConfig({plugins:[react(),tailwindcss(),VitePWA({registerType:'autoUpdate',includeAssets:['favicon.svg'],manifest:{name:'Hotel Management Platform',short_name:'Hotel Platform',description:'Offline-ready hotel operations and guest engagement platform',theme_color:'#153f32',background_color:'#f7f3e9',display:'standalone',start_url:'/',icons:[]},workbox:{navigateFallback:'/index.html',runtimeCaching:[{urlPattern:/\/api\/hotel\/settings\/$/,handler:'NetworkFirst',options:{cacheName:'hotel-settings',expiration:{maxEntries:5,maxAgeSeconds:86400}}},{urlPattern:/\/api\/rooms\/types\/$/,handler:'NetworkFirst',options:{cacheName:'public-rooms',expiration:{maxEntries:10,maxAgeSeconds:3600}}}]}})]});
