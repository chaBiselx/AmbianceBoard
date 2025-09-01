/// <reference types="vitest" />
import { defineConfig, loadEnv } from 'vite';
import { resolve } from 'path';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');

    return {
        resolve: {
            alias: {
                bootstrap: resolve(__dirname, 'node_modules/bootstrap'),
                '@': resolve(__dirname, './src')
            }
        },
        build: {
            rollupOptions: {
                dir: resolve(__dirname, 'static/js'),
                input: {
                    SoundboardPlayer: resolve(__dirname, 'src/SoundboardPlayer.ts'),
                    FormPlaylist: resolve(__dirname, 'src/FormPlaylist.ts'),
                    ListingMusiques: resolve(__dirname, 'src/ListingMusiques.ts'),
                    FormSoundboard: resolve(__dirname, 'src/FormSoundboard.ts'),
                    PasswordRules: resolve(__dirname, 'src/PasswordRules.ts'),
                    SounboardOrganizer: resolve(__dirname, 'src/SounboardOrganizer.ts'),
                    PublicFavorite: resolve(__dirname, 'src/PublicFavorite.ts'),
                    General: resolve(__dirname, 'src/General.ts'),
                    UpdateDimension: resolve(__dirname, 'src/UpdateDimension.ts'),
                    Manager_General: resolve(__dirname, 'src/ManagerGeneral.ts'),
                    ManagerEditTier: resolve(__dirname, 'src/ManagerEditTier.ts'),
                    ManagerListTier: resolve(__dirname, 'src/ManagerListTier.ts'),
                    ManagerDashboard: resolve(__dirname, 'src/ManagerDashboard.ts'),
                    Moderator_General: resolve(__dirname, 'src/ModeratorGeneral.ts'),
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
            'import.meta.env.DEBUG': env.DEBUG === '1'
        },
        test: {
            globals: true,
            environment: 'jsdom',
        },
    };
});
