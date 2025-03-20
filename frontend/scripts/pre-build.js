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
        // Déplacer les fichiers CSS
        await fs.copy(`${outputDir}/css`, `${targetDir}/css`);
        console.log('✔️ Fichiers CSS déplacés !');

        // Déplacer les images
        await fs.copy(`${outputDir}/img`, `${targetDir}/img`);
        console.log('✔️ Images déplacées !');

        // fontawesome
        await fs.copy(`node_modules/@fortawesome/fontawesome-free/css/all.min.css`, `${targetDir}/css/font-awesome.min.css`);
        await fs.copy(`node_modules/@fortawesome/fontawesome-free/webfonts/`, `${targetDir}/webfonts/`);
        console.log('✔️ FontAwesome déplacé !');
    } catch (error) {
        console.error('❌ Erreur lors du déplacement des fichiers :', error);
    }
}

moveFiles();
