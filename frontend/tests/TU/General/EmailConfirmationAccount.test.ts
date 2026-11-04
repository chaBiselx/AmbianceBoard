import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import EmailConfirmationAccount from '../../../src/modules/General/EmailConfirmationAccount';
import Notification from '../../../src/modules/General/Notifications';
import Csrf from '../../../src/modules/General/Csrf';

vi.mock('@/modules/General/Notifications', () => ({
    default: { createClientNotification: vi.fn() },
}));
vi.mock('@/modules/General/Csrf', () => ({
    default: { getToken: vi.fn() },
}));

describe('EmailConfirmationAccount', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
        vi.clearAllMocks();
        vi.mocked(Csrf.getToken).mockReturnValue('csrf-token');
    });

    afterEach(() => {
        vi.unstubAllGlobals();
        vi.restoreAllMocks();
    });

    it('sends a confirmation email and displays a success notification', async () => {
        document.body.innerHTML = '<button id="resend" data-url="/resend"></button>';
        const button = document.getElementById('resend') as HTMLButtonElement;
        const fetchMock = vi.fn().mockResolvedValue({ json: vi.fn().mockResolvedValue({}) });
        vi.stubGlobal('fetch', fetchMock);

        new EmailConfirmationAccount('resend').addEvent();
        button.click();

        expect(button.style.display).toBe('none');
        expect(fetchMock).toHaveBeenCalledWith('/resend', {
            method: 'POST',
            headers: { 'X-CSRFToken': 'csrf-token' },
        });
        await vi.waitFor(() => expect(Notification.createClientNotification).toHaveBeenCalledWith({
            message: 'Email envoyé avec success',
            type: 'success',
        }));
    });

    it('does not send a request without a URL or CSRF token', () => {
        document.body.innerHTML = '<button id="resend"></button>';
        vi.mocked(Csrf.getToken).mockReturnValue(null);
        const fetchMock = vi.fn();
        vi.stubGlobal('fetch', fetchMock);

        new EmailConfirmationAccount('resend').addEvent();
        document.getElementById('resend')!.click();

        expect(fetchMock).not.toHaveBeenCalled();
    });
});
