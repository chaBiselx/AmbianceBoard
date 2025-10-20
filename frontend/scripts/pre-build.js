import fs from 'fs-extra';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Convertit l'URL du fichier en chemin système
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const outputDir = path.resolve(__dirname, '../assets');
const targetDir = path.resolve(__dirname, '../static');

// Fonction utilitaire pour afficher le contenu du dossier
async function logDirectoryContent(dir, label) {
    try {
        const files = await fs.readdir(dir);
        console.log(`📂 Contenu de ${label} (${dir}) :`);
        if (files.length === 0) {
            console.log('   (vide)');
        } else {
            for (const f of files) {
                console.log('   -', f);
            }
        }
    } catch (err) {
        console.warn(`⚠️ Impossible de lire le dossier ${dir} :`, err.message);
    }
}

async function moveFiles() {
    console.log('🚀 Déplacement des fichiers après build...');

    // Log avant
    await logDirectoryContent(targetDir, 'avant');

    try {
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

    // Log après
    await logDirectoryContent(targetDir, 'après');
}

moveFiles();
