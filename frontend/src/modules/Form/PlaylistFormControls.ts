import ColorSoftener from '@/modules/Form/ColorSoftoner';
import { renderPlaylistPreview } from '@/modules/Form/PlaylistPreview';

const PREVIEW_INPUT_IDS = ['id_name', 'id_color', 'id_colorText', 'id_icon', 'id_typePlaylist', 'id_useSpecificColor'];

export function initializePlaylistFormControls(
    doc: Document = document,
    renderPreview: (doc: Document) => void = renderPlaylistPreview,
): void {
    toggleFormVisibility(doc, 'id_useSpecificColor', 'color_form');
    toggleFormVisibility(doc, 'id_useSpecificDelay', 'delay_form');
    renderPreview(doc);

    for (const id of PREVIEW_INPUT_IDS) {
        const input = doc.getElementById(id) as HTMLInputElement | null;
        if (!input) continue;

        const update = () => {
            if (input.type === 'color') {
                input.value = new ColorSoftener().soften(input.value);
            }
            renderPreview(doc);
        };
        input.addEventListener('input', update);
        input.addEventListener('change', update);
    }

    doc.getElementById('id_useSpecificColor')?.addEventListener('change', () => {
        toggleFormVisibility(doc, 'id_useSpecificColor', 'color_form');
    });
    doc.getElementById('id_useSpecificDelay')?.addEventListener('change', () => {
        toggleFormVisibility(doc, 'id_useSpecificDelay', 'delay_form');
    });

    const volumeInput = doc.getElementById('id_volume') as HTMLInputElement | null;
    if (volumeInput) {
        setVolumeToAllMusic(Number.parseFloat(volumeInput.value), doc);
        volumeInput.addEventListener('change', () => setVolumeToAllMusic(Number.parseFloat(volumeInput.value), doc));
    }
}

function toggleFormVisibility(doc: Document, checkboxId: string, className: string): void {
    const checkbox = doc.getElementById(checkboxId) as HTMLInputElement | null;
    for (const element of doc.getElementsByClassName(className)) {
        element.classList.toggle('d-none', !checkbox?.checked);
    }
}

function setVolumeToAllMusic(volume: number, doc: Document): void {
    for (const element of doc.querySelectorAll('.music-player')) {
        (element as HTMLAudioElement).volume = volume / 100;
    }
}