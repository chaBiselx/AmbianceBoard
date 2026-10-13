import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import OnboardingInvitation from '../../../src/modules/General/OnboardingInvitation';
import Time from '../../../src/modules/Util/Time';

describe('OnboardingInvitation', () => {
    const delay = Time.get_seconds(10);
    const storageKey = 'ambiance_onboarding_invitation';
    const instances: OnboardingInvitation[] = [];
    const createInvitation = (onStart = vi.fn()) => {
        const invitation = new OnboardingInvitation(10);
        instances.push(invitation);
        invitation.initialize(onStart);
        return invitation;
    };

    beforeEach(() => {
        vi.useFakeTimers();
        vi.setSystemTime(new Date('2026-10-11T12:00:00Z'));
        localStorage.removeItem(storageKey);
        document.body.innerHTML = '';
        document.documentElement.dataset.userAuthenticated = 'false';
        document.documentElement.lang = 'fr';
    });

    afterEach(() => {
        instances.splice(0).forEach(invitation => invitation.dispose());
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
        localStorage.removeItem(storageKey);
        delete document.documentElement.dataset.userAuthenticated;
        document.documentElement.lang = '';
        vi.useRealTimers();
    });

    it('shows the invitation only once the configured delay has elapsed', () => {
        createInvitation();
        vi.advanceTimersByTime(delay - 1);
        expect(document.querySelector('.action-notification')).toBeNull();
        vi.advanceTimersByTime(1);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        expect(document.querySelector('h2')?.textContent).toBe('D\u00e9couvrez AmbianceBoard');
        expect(document.querySelector('.action-notification-action')?.textContent).toBe('Commencer la visite');
        expect(document.querySelector('.action-notification-dismiss')?.getAttribute('aria-label')).toBe('Fermer');
    });

    it('keeps elapsed time across page loads', () => {
        const firstPage = createInvitation();
        vi.advanceTimersByTime(delay / 2);
        firstPage.dispose();
        createInvitation();
        vi.advanceTimersByTime(delay / 2 - 1);
        expect(document.querySelector('.action-notification')).toBeNull();
        vi.advanceTimersByTime(1);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
    });

    it('counts initialization time and immediately offers after an elapsed deadline', () => {
        const invitation = new OnboardingInvitation(60);
        instances.push(invitation);
        vi.advanceTimersByTime(61000);
        invitation.initialize(vi.fn());
        vi.advanceTimersByTime(0);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
    });

    it('restores a pending invitation immediately after reload without duplicate initialization', () => {
        const invitation = createInvitation();
        invitation.initialize(vi.fn());
        vi.advanceTimersByTime(delay);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        invitation.dispose();
        const reloaded = createInvitation();
        reloaded.initialize(vi.fn());
        vi.advanceTimersByTime(0);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        expect(JSON.parse(localStorage.getItem(storageKey)!).dismissed).toBe(false);
    });

    it('dismisses persistently without starting the tour', () => {
        const onStart = vi.fn();
        createInvitation(onStart);
        vi.advanceTimersByTime(60000);
        document.querySelector<HTMLButtonElement>('.action-notification-dismiss')!.click();
        createInvitation();
        vi.advanceTimersByTime(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
        expect(onStart).not.toHaveBeenCalled();
    });

    it('starts once without needing a tour button and renders English labels', () => {
        document.documentElement.lang = 'en-GB';
        const onStart = vi.fn();
        createInvitation(onStart);
        vi.advanceTimersByTime(60000);
        expect(document.querySelector('h2')?.textContent).toBe('Discover AmbianceBoard');
        expect(document.querySelector('p')?.textContent).toBe('Would you like a guided tour of AmbianceBoard?');
        expect(document.querySelector('.action-notification-dismiss')?.getAttribute('aria-label')).toBe('Close');
        const action = document.querySelector<HTMLButtonElement>('.action-notification-action')!;
        expect(action.textContent).toBe('Start the tour');
        action.click();
        action.click();
        expect(onStart).toHaveBeenCalledOnce();
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it.each(['true', '', 'invalid'])('leaves authentication eligibility to the caller for marker %s', (marker: string) => {
        document.documentElement.dataset.userAuthenticated = marker;
        createInvitation();
        vi.advanceTimersByTime(60000);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        expect(localStorage.getItem(storageKey)).not.toBeNull();
    });

    it('does not schedule a notification until the caller initializes it', () => {
        delete document.documentElement.dataset.userAuthenticated;
        const invitation = new OnboardingInvitation(10);
        instances.push(invitation);
        vi.advanceTimersByTime(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it('suppresses invitations persistently after a manual tour start', () => {
        const invitation = createInvitation();
        vi.advanceTimersByTime(10000);
        invitation.suppress();
        createInvitation();
        vi.advanceTimersByTime(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it('closes a visible invitation when suppressed', () => {
        const invitation = createInvitation();
        vi.advanceTimersByTime(60000);
        invitation.suppress();
        expect(document.getElementById('action-notification-container')).toBeNull();
    });

    it.each(['not json', 'null', '{}', '{"startedAt":"bad","prompted":false}',
        '{"startedAt":-1,"prompted":false}', '{"startedAt":9999999999999,"prompted":false}'])
    ('recovers from invalid stored state %s', (saved: string) => {
        localStorage.setItem(storageKey, saved);
        createInvitation();
        vi.advanceTimersByTime(delay - 1);
        expect(document.querySelector('.action-notification')).toBeNull();
        vi.advanceTimersByTime(1);
        expect(document.querySelector('.action-notification')).not.toBeNull();
    });

    it('still offers locally when local storage is unavailable', () => {
        vi.stubGlobal('localStorage', {
            getItem: () => { throw new Error('Storage denied'); },
            setItem: () => { throw new Error('Storage denied'); },
        });
        createInvitation();
        vi.advanceTimersByTime(60000);
        expect(document.querySelector('.action-notification')).not.toBeNull();
    });

    it('pauses on pagehide and reschedules the remaining time on pageshow', () => {
        createInvitation();
        vi.advanceTimersByTime(delay / 2);
        globalThis.dispatchEvent(new Event('pagehide'));
        vi.advanceTimersByTime(40000);
        expect(document.querySelector('.action-notification')).toBeNull();
        globalThis.dispatchEvent(new Event('pageshow'));
        vi.advanceTimersByTime(0);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
    });

    it('does not offer again on a cached page after dismissal on another page', () => {
        createInvitation();
        vi.advanceTimersByTime(delay / 2);
        globalThis.dispatchEvent(new Event('pagehide'));
        const nextPage = createInvitation();
        vi.advanceTimersByTime(delay / 2);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        document.querySelector<HTMLButtonElement>('.action-notification-dismiss')!.click();
        nextPage.dispose();
        globalThis.dispatchEvent(new Event('pageshow'));
        vi.advanceTimersByTime(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it('restores a pending invitation when returning to a cached page', () => {
        createInvitation();
        vi.advanceTimersByTime(delay);
        globalThis.dispatchEvent(new Event('pagehide'));
        expect(document.querySelector('.action-notification')).toBeNull();
        globalThis.dispatchEvent(new Event('pageshow'));
        vi.advanceTimersByTime(0);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
    });

    it('restores an invitation from the previously stored prompted state', () => {
        localStorage.setItem(storageKey, JSON.stringify({ startedAt: Date.now() - delay, prompted: true }));
        createInvitation();
        vi.advanceTimersByTime(0);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
    });
});