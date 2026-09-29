import { beforeEach, describe, expect, it, vi } from 'vitest';
import { addClearIconConfirmation } from '@/modules/ClearIconConfirmation';

const modalMocks = vi.hoisted(() => ({
    show: vi.fn((options: { footer: string }) => {
        document.body.insertAdjacentHTML('beforeend', options.footer);
    }),
    hide: vi.fn(),
    getMainHTMLElement: vi.fn(() => document.body),
}));

vi.mock('@/modules/General/Modal', () => ({ default: modalMocks }));

describe('addClearIconConfirmation', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        document.body.innerHTML = '<input id="id_clear_icon" type="checkbox">';
    });

    it('clears the checkbox when the confirmation is cancelled', () => {
        const checkbox = document.getElementById('id_clear_icon') as HTMLInputElement;
        addClearIconConfirmation('playlist');
        checkbox.checked = true;
        checkbox.dispatchEvent(new Event('change'));

        expect(modalMocks.show).toHaveBeenCalledWith(expect.objectContaining({
            body: "<p>Êtes-vous sûr de vouloir supprimer l'icône playlist ?</p>",
            width: 'sm',
        }));
        document.getElementById('clear-icon-cancel')!.click();
        document.body.dispatchEvent(new Event('hidden.bs.modal'));

        expect(modalMocks.hide).toHaveBeenCalledOnce();
        expect(checkbox.checked).toBe(false);
    });

    it('keeps the checkbox checked when deletion is confirmed', () => {
        const checkbox = document.getElementById('id_clear_icon') as HTMLInputElement;
        addClearIconConfirmation('soundboard');
        checkbox.checked = true;
        checkbox.dispatchEvent(new Event('change'));

        document.getElementById('clear-icon-confirm')!.click();
        document.body.dispatchEvent(new Event('hidden.bs.modal'));

        expect(modalMocks.hide).toHaveBeenCalledOnce();
        expect(checkbox.checked).toBe(true);
    });

    it('does nothing when the clear-icon control is absent', () => {
        document.body.innerHTML = '';

        expect(() => addClearIconConfirmation('playlist')).not.toThrow();
        expect(modalMocks.show).not.toHaveBeenCalled();
    });
});