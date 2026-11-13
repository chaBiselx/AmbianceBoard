import { beforeEach, describe, expect, it, vi } from 'vitest';
import DeleteAccount from '../../../src/modules/General/DeleteAccount';
import Notification from '../../../src/modules/General/Notifications';
import ConsoleTraceServeur from '../../../src/modules/General/ConsoleTraceServeur';
import Csrf from '../../../src/modules/General/Csrf';
import { setupAccountTestHooks } from './accountTestSetup';

vi.mock('@/modules/General/Notifications', () => ({
    default: { createClientNotification: vi.fn() },
}));
vi.mock('@/modules/General/ConsoleTraceServeur', () => ({
    default: { error: vi.fn() },
}));
vi.mock('@/modules/General/Csrf', () => ({
    default: { getToken: vi.fn() },
}));

describe('DeleteAccount', () => {
    beforeEach(() => {
        document.body.innerHTML = '<form method="DELETE" action="/delete"><button id="delete-account"></button></form>';
    });
    setupAccountTestHooks();

    it('asks for confirmation and redirects after a successful deletion', async () => {
        const confirmMock = vi.fn().mockReturnValue(true);
        const fetchMock = vi.fn().mockResolvedValue({ ok: true });
        const formUrl = (document.querySelector('form') as HTMLFormElement).action;
        vi.stubGlobal('confirm', confirmMock);
        vi.stubGlobal('fetch', fetchMock);
        vi.stubGlobal('location', { href: 'http://localhost/' });
        new DeleteAccount().addEvent();

        document.getElementById('delete-account')!.dispatchEvent(new MouseEvent('click', { cancelable: true }));

        expect(confirmMock).toHaveBeenCalledWith('Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.');
        expect(fetchMock).toHaveBeenCalledWith(formUrl, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': 'csrf-token' },
        });
        await vi.waitFor(() => expect(globalThis.location.href).toBe('/'));
    });

    it('does not send a request when deletion is cancelled', () => {
        vi.stubGlobal('confirm', vi.fn().mockReturnValue(false));
        const fetchMock = vi.fn();
        vi.stubGlobal('fetch', fetchMock);
        new DeleteAccount().addEvent();
        const event = new MouseEvent('click', { cancelable: true });

        document.getElementById('delete-account')!.dispatchEvent(event);

        expect(event.defaultPrevented).toBe(true);
        expect(fetchMock).not.toHaveBeenCalled();
    });

    it('shows an error notification when the deletion request is rejected', async () => {
        vi.stubGlobal('confirm', vi.fn().mockReturnValue(true));
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }));
        new DeleteAccount().addEvent();

        document.getElementById('delete-account')!.click();

        await vi.waitFor(() => expect(Notification.createClientNotification).toHaveBeenCalledWith({
            message: 'Une erreur est survenue',
            type: 'danger',
        }));
    });

    it('logs a failed deletion request', async () => {
        const error = new Error('network error');
        vi.stubGlobal('confirm', vi.fn().mockReturnValue(true));
        vi.stubGlobal('fetch', vi.fn().mockRejectedValue(error));
        new DeleteAccount().addEvent();

        document.getElementById('delete-account')!.click();

        await vi.waitFor(() => expect(ConsoleTraceServeur.error).toHaveBeenCalledWith('Failed to delete account:', error));
    });
});
