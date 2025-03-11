import { defineConfig, loadEnv } from 'vite';
import { resolve } from 'path';

export default defineConfig(({ mode }) => {
    // Charge les variables d'environnement en fonction du mode
    const env = loadEnv(mode, process.cwd(), '');

    return {
        build: {
            rollupOptions: {
                input: {
                    SoundboardPlayer: resolve(__dirname, 'src/SoundboardPlayer.ts'),
                    FormPlaylist: resolve(__dirname, 'src/FormPlaylist.ts'),
                    FormSoundboard: resolve(__dirname, 'src/FormSoundboard.ts'),
                    PasswordRules: resolve(__dirname, 'src/PasswordRules.ts'),
                    SounboardOrganizer: resolve(__dirname, 'src/SounboardOrganizer.ts')
                },
                output: {
                    format: 'es',
                    entryFileNames: '[name].[hash].js',
                    chunkFileNames: '[name].[hash].js',
                    assetFileNames: '[name].[hash].[ext]'
                }
            }
        },
        define: {
            // Expose DEBUG spécifiquement
            'import.meta.env.DEBUG': env.DEBUG === '1'
        }
    };
});