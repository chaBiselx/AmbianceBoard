import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';

// Convertit l'URL du fichier en chemin système
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const outputDir = path.resolve(__dirname, '../assets');
const targetDir = path.resolve(__dirname, '../static');

async function moveFiles() {
    console.log('🚀 Déplacement des fichiers après build...');

    try {
        await fs.copy(`${outputDir}/js`, `${targetDir}/js_pure`);
        console.log('✔️ Fichiers JS déplacés !');

        await fs.copy(`${outputDir}/css`, `${targetDir}/css`);
        console.log('✔️ Fichiers CSS déplacés !');

        await fs.copy(`${outputDir}/img`, `${targetDir}/img`);
        console.log('✔️ Images déplacées !');
    } catch (error) {
        console.error('❌ Erreur lors du déplacement des fichiers :', error);
    }
}

moveFiles();