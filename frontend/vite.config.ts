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
                    FormSoundboard: resolve(__dirname, 'src/FormSoundboard.ts'),
                    PasswordRules: resolve(__dirname, 'src/PasswordRules.ts'),
                    SounboardOrganizer: resolve(__dirname, 'src/SounboardOrganizer.ts'),
                    General: resolve(__dirname, 'src/General.ts'),
                    UpdateDimension: resolve(__dirname, 'src/UpdateDimension.ts'),
                    Manager_General: resolve(__dirname, 'src/ManagerGeneral.ts'),
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
        }
    };
});
