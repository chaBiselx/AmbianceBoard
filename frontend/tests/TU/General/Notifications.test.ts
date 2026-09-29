import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import Notification from '../../../src/modules/General/Notifications';

describe('Notification.createClientNotification', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        document.body.innerHTML = '';
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('should create a notification container and a notification with default options', () => {
        Notification.createClientNotification();

        const container = document.getElementById('notification-container');
        expect(container).not.toBeNull();
        const notification = container!.firstElementChild as HTMLElement;
        expect(notification.innerText).toBe('Notification');
        expect(notification.className).toBe('bg-info fade show');
    });

    it('should reuse an existing notification container', () => {
        Notification.createClientNotification({ message: 'first' });
        Notification.createClientNotification({ message: 'second' });

        const containers = document.querySelectorAll('#notification-container');
        expect(containers).toHaveLength(1);
        expect(containers[0].children).toHaveLength(2);
    });

    it('should apply custom options', () => {
        Notification.createClientNotification({ message: 'Custom', type: 'danger', duration: 1000 });

        const container = document.getElementById('notification-container')!;
        const notification = container.firstElementChild as HTMLElement;
        expect(notification.innerText).toBe('Custom');
        expect(notification.className).toBe('bg-danger fade show');
    });

    it('should fade out and remove the notification after the configured duration', () => {
        Notification.createClientNotification({ duration: 500 });
        const container = document.getElementById('notification-container')!;
        const notification = container.firstElementChild as HTMLElement;

        vi.advanceTimersByTime(500);
        expect(notification.classList.contains('fade')).toBe(true);
        expect(notification.classList.contains('show')).toBe(false);

        vi.advanceTimersByTime(150);
        expect(container.contains(notification)).toBe(false);
    });

    it('should fade out immediately when the notification is clicked', () => {
        Notification.createClientNotification({ duration: 3000 });
        const container = document.getElementById('notification-container')!;
        const notification = container.firstElementChild as HTMLElement;

        notification.dispatchEvent(new Event('click'));
        expect(notification.classList.contains('fade')).toBe(true);

        vi.advanceTimersByTime(150);
        expect(container.contains(notification)).toBe(false);
    });
});
