import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        SoundboardPlayer: resolve(__dirname, 'src/SoundboardPlayer.ts'),
        FormPlaylist: resolve(__dirname, 'src/FormPlaylist.ts'),
        PasswordRules: resolve(__dirname, 'src/PasswordRules.ts')
      },
      output: {
        format: 'es',
        entryFileNames: '[name].[hash].js',
        chunkFileNames: '[name].[hash].js',
        assetFileNames: '[name].[hash].[ext]'
      }
    }
  }
});