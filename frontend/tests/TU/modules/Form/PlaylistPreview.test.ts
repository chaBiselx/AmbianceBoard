import { beforeEach, describe, expect, it } from 'vitest';
import { renderPlaylistPreview } from '@/modules/Form/PlaylistPreview';

describe('PlaylistPreview', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div id="demo-playlist"></div>
            <input id="id_name" value="&lt;img src=x onerror=alert(1)&gt;">
            <input id="id_useSpecificColor" type="checkbox">
            <input id="id_typePlaylist" value="ambiance">
            <input id="default_ambiance_color" value="#123456">
            <input id="default_ambiance_colorText" value="#ffffff">
        `;
    });

    it('renders default colors and treats the playlist name as text', () => {
        renderPlaylistPreview();

        const preview = document.getElementById('demo-playlist')!;
        expect(preview.textContent).toBe('<img src=x onerror=alert(1)>');
        expect(preview.querySelector('img')).toBeNull();
        expect(preview.style.backgroundColor).toBe('rgb(18, 52, 86)');
        expect(preview.style.color).toBe('rgb(255, 255, 255)');
    });

    it('uses custom colors when enabled', () => {
        document.body.insertAdjacentHTML('beforeend', `
            <input id="id_color" value="#abcdef">
            <input id="id_colorText" value="#010203">
        `);
        (document.getElementById('id_useSpecificColor') as HTMLInputElement).checked = true;

        renderPlaylistPreview();

        const preview = document.getElementById('demo-playlist')!;
        expect(preview.style.backgroundColor).toBe('rgb(171, 205, 239)');
        expect(preview.style.color).toBe('rgb(1, 2, 3)');
    });
});