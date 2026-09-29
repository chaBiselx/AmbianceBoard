import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import NotificationGeneral from '../../../src/modules/General/NotificationGeneral';
import Csrf from '../../../src/modules/General/Csrf';

vi.mock('@/modules/General/Csrf', () => ({
    default: { getToken: vi.fn() },
}));

function clearAllCookies() {
    document.cookie.split(';').forEach((cookie) => {
        const name = cookie.split('=')[0].trim();
        if (name) {
            document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
        }
    });
}

function createNotification(uuid: string, extra: Record<string, string> = {}) {
    const alert = document.createElement('div');
    alert.className = 'alert';
    const button = document.createElement('button');
    button.className = 'close-notification';
    button.dataset.metaUuid = uuid;
    Object.entries(extra).forEach(([key, value]) => {
        button.dataset[key] = value;
    });
    alert.appendChild(button);
    return { alert, button };
}

describe('NotificationGeneral', () => {
    beforeEach(() => {
        clearAllCookies();
        document.body.innerHTML = '<div id="notifications-general"></div>';
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should do nothing when the notifications section is missing', () => {
        document.body.innerHTML = '';
        expect(() => new NotificationGeneral().addEvent()).not.toThrow();
    });

    it('should remove an already dismissed notification for an anonymous user', () => {
        document.cookie = `dismissed_general_notifications=${encodeURIComponent(JSON.stringify(['uuid-1']))}`;
        const section = document.getElementById('notifications-general')!;
        const { alert } = createNotification('uuid-1');
        section.appendChild(alert);

        new NotificationGeneral().addEvent();

        expect(section.querySelector('.alert')).toBeNull();
    });

    it('should keep a notification that was not previously dismissed', () => {
        const section = document.getElementById('notifications-general')!;
        const { alert } = createNotification('uuid-2');
        section.appendChild(alert);

        new NotificationGeneral().addEvent();

        expect(section.querySelector('.alert')).not.toBeNull();
    });

    it('should skip the dismissed check when the close button has no notification uuid', () => {
        const section = document.getElementById('notifications-general')!;
        const alert = document.createElement('div');
        alert.className = 'alert';
        const button = document.createElement('button');
        button.className = 'close-notification';
        alert.appendChild(button);
        section.appendChild(alert);

        expect(() => new NotificationGeneral().addEvent()).not.toThrow();
        expect(section.querySelector('.alert')).not.toBeNull();
    });

    it('should ignore a malformed dismissed-notifications cookie', () => {
        document.cookie = 'dismissed_general_notifications=not-json';
        const section = document.getElementById('notifications-general')!;
        const { alert } = createNotification('uuid-3');
        section.appendChild(alert);

        new NotificationGeneral().addEvent();

        expect(section.querySelector('.alert')).not.toBeNull();
    });

    it('should ignore a dismissed-notifications cookie that is not an array', () => {
        document.cookie = `dismissed_general_notifications=${encodeURIComponent(JSON.stringify({ a: 1 }))}`;
        const section = document.getElementById('notifications-general')!;
        const { alert } = createNotification('uuid-4');
        section.appendChild(alert);

        new NotificationGeneral().addEvent();

        expect(section.querySelector('.alert')).not.toBeNull();
    });

    it('should dismiss a notification client-side and persist the uuid in a cookie', () => {
        const section = document.getElementById('notifications-general')!;
        const { alert, button } = createNotification('uuid-6');
        section.appendChild(alert);

        const notification = new NotificationGeneral();
        notification.addEvent();
        button.dispatchEvent(new Event('click', { bubbles: true }));

        expect(section.querySelector('.alert')).toBeNull();
        expect(document.cookie).toContain('dismissed_general_notifications=');
    });

    it('should not duplicate the same uuid when dismissed twice', () => {
        const section = document.getElementById('notifications-general')!;
        const first = createNotification('uuid-7');
        const second = createNotification('uuid-7');
        section.appendChild(first.alert);
        section.appendChild(second.alert);

        const notification = new NotificationGeneral();
        notification.addEvent();
        first.button.dispatchEvent(new Event('click', { bubbles: true }));
        second.button.dispatchEvent(new Event('click', { bubbles: true }));

        const match = document.cookie.match(/dismissed_general_notifications=([^;]+)/);
        const values = JSON.parse(decodeURIComponent(match![1]));
        expect(values).toEqual(['uuid-7']);
    });

    it('should notify the server when a notification has a dismiss url', () => {
        vi.mocked(Csrf.getToken).mockReturnValue('csrf-token');
        globalThis.fetch = vi.fn().mockResolvedValue({});
        const section = document.getElementById('notifications-general')!;
        const { alert, button } = createNotification('uuid-8', { metaUrl_dismiss: '/dismiss/8' });
        section.appendChild(alert);

        const notification = new NotificationGeneral();
        notification.addEvent();
        button.dispatchEvent(new Event('click', { bubbles: true }));

        expect(globalThis.fetch).toHaveBeenCalledWith(
            '/dismiss/8',
            expect.objectContaining({ method: 'POST', headers: expect.objectContaining({ 'X-CSRFToken': 'csrf-token' }) })
        );
    });

    it('should not call the server when the csrf token is missing', () => {
        vi.mocked(Csrf.getToken).mockReturnValue(null);
        globalThis.fetch = vi.fn();
        const section = document.getElementById('notifications-general')!;
        const { alert, button } = createNotification('uuid-9', { metaUrl_dismiss: '/dismiss/9' });
        section.appendChild(alert);

        const notification = new NotificationGeneral();
        notification.addEvent();
        button.dispatchEvent(new Event('click', { bubbles: true }));

        expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it('should ignore clicks on a child element of the close button', () => {
        const section = document.getElementById('notifications-general')!;
        const { alert, button } = createNotification('uuid-10');
        const icon = document.createElement('i');
        button.appendChild(icon);
        section.appendChild(alert);

        const notification = new NotificationGeneral();
        notification.addEvent();
        icon.dispatchEvent(new Event('click', { bubbles: true }));

        expect(section.querySelector('.alert')).not.toBeNull();
    });
});
