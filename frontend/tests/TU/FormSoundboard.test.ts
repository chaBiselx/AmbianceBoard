import { beforeEach, describe, expect, it, vi } from 'vitest';

const soundboardFormMocks = vi.hoisted(() => ({
    csrf: vi.fn(),
    error: vi.fn(),
    clearConfirmation: vi.fn(),
    tagSelectorInit: vi.fn(),
    soften: vi.fn(),
}));

vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: soundboardFormMocks.csrf } }));
vi.mock('@/modules/General/ConsoleCustom', () => ({ default: { error: soundboardFormMocks.error } }));
vi.mock('@/modules/ClearIconConfirmation', () => ({ addClearIconConfirmation: soundboardFormMocks.clearConfirmation }));
vi.mock('@/modules/Form/TagSelector', () => ({ default: class { init() { soundboardFormMocks.tagSelectorInit(); } } }));
vi.mock('@/modules/Form/ColorSoftoner', () => ({ default: class { soften(value: string) { return soundboardFormMocks.soften(value); } } }));

describe('FormSoundboard page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        soundboardFormMocks.csrf.mockReturnValue('csrf-token');
        soundboardFormMocks.soften.mockReturnValue('#00ff00');
        document.body.innerHTML = `
            <input id="id_name" value="Ambient board">
            <input id="id_color" type="color" value="#112233">
            <input id="id_colorText" type="color" value="#ffffff">
            <input id="id_icon" type="text" value="">
            <input id="id_clear_icon" type="checkbox">
            <div id="demo-soundboard"></div>
            <button id="btn-delete-soundboard" data-deleteurl="/delete" data-redirecturl="/boards"></button>
        `;
    });

    it('updates the live preview and handles cancelled and failed deletion', async () => {
        const fetchMock = vi.fn().mockResolvedValue({ status: 500 });
        vi.stubGlobal('fetch', fetchMock);
        const confirmMock = vi.fn().mockReturnValue(false);
        vi.stubGlobal('confirm', confirmMock);
        const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

        await import('@/FormSoundboard');
        const demo = document.getElementById('demo-soundboard')!;
        expect(demo.textContent).toBe('Ambient board');
        expect(demo.style.backgroundColor).toBe('rgb(17, 34, 51)');
        expect(demo.style.color).toBe('rgb(255, 255, 255)');
        expect(soundboardFormMocks.clearConfirmation).toHaveBeenCalledWith('du soundboard');

        const color = document.getElementById('id_color') as HTMLInputElement;
        color.value = '#ff0000';
        color.dispatchEvent(new Event('input'));
        expect(soundboardFormMocks.soften).toHaveBeenCalledWith('#ff0000');
        expect(color.value).toBe('#00ff00');
        expect(demo.style.backgroundColor).toBe('rgb(0, 255, 0)');

        const existingIcon = document.createElement('a');
        existingIcon.id = 'id_icon_alreadyexist';
        existingIcon.href = '/media/icon.png';
        document.body.appendChild(existingIcon);
        document.getElementById('id_name')!.dispatchEvent(new Event('change'));
        expect(demo.querySelector('img')!.getAttribute('src')).toBe(existingIcon.href);

        document.dispatchEvent(new Event('DOMContentLoaded'));
        expect(soundboardFormMocks.tagSelectorInit).toHaveBeenCalledOnce();
        const deleteButton = document.getElementById('btn-delete-soundboard')!;
        deleteButton.click();
        expect(fetchMock).not.toHaveBeenCalled();

        confirmMock.mockReturnValue(true);
        deleteButton.click();
        await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/delete', expect.objectContaining({ method: 'DELETE' })));
        expect(fetchMock).toHaveBeenCalledWith('/delete', expect.objectContaining({
            headers: { 'X-CSRFToken': 'csrf-token' },
        }));
        expect(consoleError).toHaveBeenCalledWith('Erreur lors de la suppression');
    });
});