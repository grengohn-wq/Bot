#!/usr/bin/env node

import { build } from 'vite';
import { resolve } from 'path';

async function buildApp() {
  try {
    console.log('🚀 Building منهج AI Mini App...');
    
    await build({
      root: resolve(process.cwd()),
      build: {
        outDir: 'dist',
        emptyOutDir: true,
        sourcemap: false,
        minify: 'terser',
        target: 'es2020',
        rollupOptions: {
          output: {
            manualChunks: {
              vendor: ['react', 'react-dom'],
              telegram: ['@tma.js/sdk-react'],
              ui: ['framer-motion', 'lucide-react'],
              store: ['zustand'],
              supabase: ['@supabase/supabase-js']
            },
            entryFileNames: 'assets/[name]-[hash].js',
            chunkFileNames: 'assets/[name]-[hash].js',
            assetFileNames: 'assets/[name]-[hash].[ext]'
          }
        },
        chunkSizeWarningLimit: 1000
      }
    });
    
    console.log('✅ Build completed successfully!');
    console.log('📦 Output directory: dist/');
    
  } catch (error) {
    console.error('❌ Build failed:', error);
    process.exit(1);
  }
}

buildApp();