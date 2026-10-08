import ModalCustom from '@/modules/General/Modal';
import { MusicDropzoneConfig, MusicDropzoneManager } from '@/modules/MusicDropzoneManager';
import Csrf from './modules/General/Csrf';
import ConsoleCustom from "./modules/General/ConsoleCustom";
import { addClearIconConfirmation } from '@/modules/ClearIconConfirmation';
import MergedFadePreviewCanvasRenderer from '@/modules/MergedFadePreviewCanvasRenderer';
import TagSelector from '@/modules/Form/TagSelector';
import { renderPlaylistPreview } from '@/modules/Form/PlaylistPreview';
import { initializePlaylistFormControls } from '@/modules/Form/PlaylistFormControls';
import { initializePlaylistColorSelector } from '@/modules/Form/PlaylistColorSelector';
import { initializePlaylistEntityActions } from '@/modules/Form/PlaylistEntityActions';



declare global {
    interface Window {
        Dropzone: any;
        musicDropzoneManager?: MusicDropzoneManager;
    }
}


const mergedFadePreviewCanvasRenderer = new MergedFadePreviewCanvasRenderer();
const renderMergedFadePreview = () => mergedFadePreviewCanvasRenderer.renderFromDom();

initializePlaylistFormControls(document, renderPlaylistPreview);


document.addEventListener("DOMContentLoaded", () => {
    addMusicEvent();
    initializePlaylistEntityActions({
        fetch: (input, init) => fetch(input, init),
        getCsrfToken: () => Csrf.getToken(),
        confirm: message => globalThis.confirm(message),
        redirect: url => { globalThis.location.href = url; },
        error: (message, error) => ConsoleCustom.error(message, error),
    });
    addPopupDescriptionPlaylistType();
    initializePlaylistColorSelector({
        fetch: (input, init) => fetch(input, init),
        showModal: options => ModalCustom.show(options),
        hideModal: () => ModalCustom.hide(),
        renderPreview: () => renderPlaylistPreview(),
        log: message => ConsoleCustom.log(message),
        error: (message, error) => ConsoleCustom.error(message, error),
    });
    addClearIconConfirmation('de la playlist');
    mergedFadePreviewCanvasRenderer.enableAutoRefresh();
    window.addEventListener('load', renderMergedFadePreview, { once: true });
    window.addEventListener('resize', renderMergedFadePreview);

    document.getElementById('id_typePlaylist')?.addEventListener('change', renderMergedFadePreview);
    document.getElementById('id_fadeIn')?.addEventListener('change', renderMergedFadePreview);
    document.getElementById('id_fadeOut')?.addEventListener('change', renderMergedFadePreview);
    (new TagSelector()).init();
});

function addPopupDescriptionPlaylistType() {
    const typePlaylistDescriptionBtn = document.getElementById('btn-show-description-playlist-type');
    if (typePlaylistDescriptionBtn) {
        typePlaylistDescriptionBtn.addEventListener('click', showDescriptionType);
    }
}

function showDescriptionType(e: Event) {
    const element = e.target as HTMLButtonElement;
    const url = element.dataset.url!;
    const title = "Selectionner Couleur existantes";

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            ModalCustom.show({
                title: title,
                body: body,
                footer: "",
                width: "lg"
            })
        })
        .catch(error => {
            ConsoleCustom.error('Erreur lors de la requête AJAX:', error);
        });
}

function addMusicEvent() {
    const addMusicBtnList = document.getElementsByClassName('btn-add-music');
    if (addMusicBtnList) {
        for (const addMusicBtn of addMusicBtnList) {
            addMusicBtn.addEventListener('click', showPopupMusic);
        }
    }
}

function showPopupMusic(event: Event) {
    const el = event.target as HTMLButtonElement;;
    const url = el.dataset.url!;
    const title = el.title;

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            ModalCustom.show({
                title: title,
                body: body,
                footer: "",
                width: "lg",
                callback: () => {
                    const dropZone = document.getElementById('music-dropzone');
                    if (dropZone) {
                        const uploadUrl = dropZone.dataset.uploadUrl;
                        const csrf = Csrf.getToken();


                        if (!uploadUrl) {
                            ConsoleCustom.error('Missing required configuration for MusicDropzoneManager');
                            return;
                        }

                        try {
                            (globalThis as typeof globalThis & { musicDropzoneManager?: MusicDropzoneManager }).musicDropzoneManager = new MusicDropzoneManager(
                                {
                                    containerSelector: '#music-dropzone',
                                    uploadUrl: uploadUrl,
                                    csrf: csrf,
                                    fileFormat: dropZone.dataset.format,
                                    nbfile: Number.parseInt(dropZone.dataset.musicremaining!),
                                    refreshAfterUpload: true
                                } as MusicDropzoneConfig);
                        } catch (error) {
                            ConsoleCustom.error('Error initializing MusicDropzoneManager:', error);
                        }
                    }
                    const fileInput = document.getElementById('id_file');
                    if (fileInput) {
                        fileInput.addEventListener('change', autoSetAlternateName);
                    }
                }
            })


        })
        .catch(error => {
            ConsoleCustom.error('Erreur lors de la requête AJAX:', error);
        });
}

function autoSetAlternateName(event: Event) {
    const fileInputOrigin = event.target as HTMLInputElement;
    const fileDest = document.getElementById('id_alternativeName') as HTMLInputElement;
    if (fileDest && fileInputOrigin && fileDest.value == '') {
        const regexFileExtension = /\.[^.]*$/g;
        if (fileInputOrigin.files?.[0]) {
            fileDest.value = fileInputOrigin.files[0].name.replace(regexFileExtension, '').substring(0, 50);
        }
    }

}