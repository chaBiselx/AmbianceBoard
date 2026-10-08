import { beforeEach, describe, expect, it, vi } from 'vitest';
import { initializePlaylistFormControls } from '@/modules/Form/PlaylistFormControls';

describe('PlaylistFormControls', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <input id="id_useSpecificColor" type="checkbox">
            <input id="id_useSpecificDelay" type="checkbox" checked>
            <input id="id_name" value="Playlist">
            <input id="id_volume" value="75">
            <div class="color_form d-none"></div>
            <div class="delay_form d-none"></div>
            <audio class="music-player"></audio>
        `;
    });

    it('binds preview fields, conditional sections, and shared music volume', () => {
        const renderPreview = vi.fn();
        initializePlaylistFormControls(document, renderPreview);
        const colorSection = document.querySelector('.color_form')!;
        const delaySection = document.querySelector('.delay_form')!;
        const audio = document.querySelector<HTMLAudioElement>('.music-player')!;

        expect(renderPreview).toHaveBeenCalledWith(document);
        expect(colorSection.classList.contains('d-none')).toBe(true);
        expect(delaySection.classList.contains('d-none')).toBe(false);
        expect(audio.volume).toBe(0.75);

        const name = document.getElementById('id_name')!;
        name.dispatchEvent(new Event('input'));
        expect(renderPreview).toHaveBeenCalledTimes(2);

        const specificColor = document.getElementById('id_useSpecificColor') as HTMLInputElement;
        specificColor.checked = true;
        specificColor.dispatchEvent(new Event('change'));
        expect(colorSection.classList.contains('d-none')).toBe(false);

        const specificDelay = document.getElementById('id_useSpecificDelay') as HTMLInputElement;
        specificDelay.checked = false;
        specificDelay.dispatchEvent(new Event('change'));
        expect(delaySection.classList.contains('d-none')).toBe(true);

        const volume = document.getElementById('id_volume') as HTMLInputElement;
        volume.value = '25';
        volume.dispatchEvent(new Event('change'));
        expect(audio.volume).toBe(0.25);
    });
});