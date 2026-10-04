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

describe('Notification.createActionNotification', () => {
    const options = () => ({
        title: 'Welcome',
        message: '<b>A guided tour?</b>',
        actionLabel: 'Start the tour',
        dismissLabel: 'Close',
        onAction: vi.fn(),
        onDismiss: vi.fn(),
    });

    beforeEach(() => {
        vi.useFakeTimers();
        document.body.innerHTML = '';
    });

    afterEach(() => vi.useRealTimers());

    it('renders safe text and accessible controls in a separate persistent container', () => {
        Notification.createClientNotification({ message: 'Existing toast' });
        Notification.createActionNotification(options());
        const container = document.getElementById('action-notification-container')!;
        expect(container.className).toBe('action-notification-container');
        expect(container.querySelector('[role="status"]')?.getAttribute('aria-live')).toBe('polite');
        expect(container.querySelector('p')?.textContent).toBe('<b>A guided tour?</b>');
        expect(container.querySelector('b')).toBeNull();
        expect(container.querySelector('[aria-label="Close"]')).not.toBeNull();
        container.querySelector('p')!.click();
        vi.advanceTimersByTime(60000);
        expect(container.isConnected).toBe(true);
        expect(document.getElementById('notification-container')).not.toBeNull();
    });

    it('executes the action only once and removes the empty container', () => {
        const config = options();
        Notification.createActionNotification(config);
        const action = document.querySelector<HTMLButtonElement>('.action-notification-action')!;
        action.click();
        action.click();
        expect(config.onAction).toHaveBeenCalledOnce();
        expect(config.onDismiss).not.toHaveBeenCalled();
        expect(document.getElementById('action-notification-container')).toBeNull();
    });

    it('dismisses without launching the tour', () => {
        const config = options();
        Notification.createActionNotification(config);
        document.querySelector<HTMLButtonElement>('[aria-label="Close"]')!.click();
        expect(config.onAction).not.toHaveBeenCalled();
        expect(config.onDismiss).toHaveBeenCalledOnce();
        expect(document.getElementById('action-notification-container')).toBeNull();
    });

    it('allows idempotent programmatic closure without removing other invitations', () => {
        const config = options();
        const first = Notification.createActionNotification(config);
        const second = Notification.createActionNotification(options());
        first.close();
        first.close();
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        expect(config.onAction).not.toHaveBeenCalled();
        expect(config.onDismiss).not.toHaveBeenCalled();
        second.close();
        expect(document.getElementById('action-notification-container')).toBeNull();
    });
});
