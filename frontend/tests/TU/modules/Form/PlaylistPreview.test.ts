import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { renderPlaylistPreview } from '@/modules/Form/PlaylistPreview';

describe('PlaylistPreview', () => {
    afterEach(() => {
        vi.unstubAllGlobals();
    });

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

    it('does not render a non-string FileReader result', () => {
        class MockFileReader {
            result: string | ArrayBuffer | null = new ArrayBuffer(1);
            private loadListener: (() => void) | null = null;

            addEventListener(_type: string, listener: () => void): void {
                this.loadListener = listener;
            }

            readAsDataURL(): void {
                this.loadListener?.();
            }
        }

        vi.stubGlobal('FileReader', MockFileReader);
        document.body.insertAdjacentHTML('beforeend', '<input id="id_icon" type="file">');
        const iconInput = document.getElementById('id_icon')!;
        Object.defineProperty(iconInput, 'files', { value: [new File([], 'icon.png')] });

        renderPlaylistPreview();

        expect(document.querySelector('#demo-playlist img')).toBeNull();
    });
});