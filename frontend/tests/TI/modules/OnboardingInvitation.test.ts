import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import OnboardingManager from '@/modules/OnboardingManager';
import OnboardingInvitation from '@/modules/General/OnboardingInvitation';
import Time from '@/modules/Util/Time';

const tourMocks = vi.hoisted(() => ({
    initialize: vi.fn(), start: vi.fn(), reset: vi.fn(), goToStep: vi.fn(), show: vi.fn(),
    shouldStartTour: vi.fn(), available: true, steps: [{}],
}));

vi.mock('@/modules/OnboardingShepherd', () => ({
    OnboardingShepherd: {
        getInstance: () => ({
            initialize: tourMocks.initialize, start: tourMocks.start, reset: tourMocks.reset,
            goToStep: tourMocks.goToStep, shouldStartTour: tourMocks.shouldStartTour,
            getShepherdTour: () => tourMocks.available ? { show: tourMocks.show, steps: tourMocks.steps } : null,
        }),
    },
}));

vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: { log: vi.fn(), warn: vi.fn(), error: vi.fn() },
}));

describe('OnboardingInvitation integration', () => {
    const delay = Time.get_seconds(30);
    const invitations: OnboardingInvitation[] = [];
    const context = {
        locale: 'fr', labels: { next: 'Suivant', prev: 'Precedent', done: 'Terminer' },
        steps: [{ id: 'private_soundboard_mixer', selector: '#target', description: 'Mixer' }],
        feature_flags: { onboarding_enabled: true },
    };

    beforeEach(() => {
        vi.useFakeTimers();
        vi.setSystemTime(new Date('2026-10-11T12:00:00Z'));
        vi.clearAllMocks();
        sessionStorage.clear();
        localStorage.removeItem('ambiance_onboarding_invitation');
        document.documentElement.dataset.userAuthenticated = 'false';
        document.documentElement.lang = 'fr';
        document.body.innerHTML = '<div id="target"></div>';
        tourMocks.available = true;
        tourMocks.steps = [{}];
        tourMocks.shouldStartTour.mockReturnValue(true);
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => context }));
        const initialize = OnboardingInvitation.prototype.initialize;
        vi.spyOn(OnboardingInvitation.prototype, 'initialize').mockImplementation(function (onStart) {
            invitations.push(this);
            initialize.call(this, onStart);
        });
    });

    afterEach(() => {
        invitations.splice(0).forEach(invitation => invitation.dispose());
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
        sessionStorage.clear();
        localStorage.removeItem('ambiance_onboarding_invitation');
        delete document.documentElement.dataset.userAuthenticated;
        document.documentElement.lang = '';
        vi.useRealTimers();
    });

    const initialize = async () => {
        const manager = new OnboardingManager();
        const promise = manager.initialize();
        await vi.advanceTimersByTimeAsync(300);
        await promise;
        return manager;
    };

    it('waits the configured delay then launches the same tour without an onboarding button', async () => {
        const manager = await initialize();
        await manager.initialize();
        expect(tourMocks.initialize).toHaveBeenCalledWith(expect.objectContaining({ isAuthenticated: true }));
        expect(tourMocks.start).not.toHaveBeenCalled();
        await vi.advanceTimersByTimeAsync(delay - 301);
        expect(document.querySelector('.action-notification')).toBeNull();
        await vi.advanceTimersByTimeAsync(1);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        document.querySelector<HTMLButtonElement>('.action-notification-action')!.click();
        expect(tourMocks.reset).toHaveBeenCalledOnce();
        expect(tourMocks.goToStep).toHaveBeenCalledWith(0);
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it('preserves elapsed time across navigation and does not offer again after dismissal', async () => {
        await initialize();
        await vi.advanceTimersByTimeAsync(delay / 2 - 300);
        invitations.splice(0).forEach(invitation => invitation.dispose());
        document.body.innerHTML = '<div id="target"></div>';
        await initialize();
        await vi.advanceTimersByTimeAsync(delay / 2 - 301);
        expect(document.querySelector('.action-notification')).toBeNull();
        await vi.advanceTimersByTimeAsync(1);
        document.querySelector<HTMLButtonElement>('.action-notification-dismiss')!.click();
        await initialize();
        await vi.advanceTimersByTimeAsync(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
        expect(tourMocks.goToStep).not.toHaveBeenCalled();
    });

    it('restores the pending notification on reload and stops restoring it after acceptance', async () => {
        await initialize();
        await vi.advanceTimersByTimeAsync(delay - 300);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        const startedAt = JSON.parse(localStorage.getItem('ambiance_onboarding_invitation')!).startedAt;
        invitations.splice(0).forEach(invitation => invitation.dispose());
        document.body.innerHTML = '<div id="target"></div>';

        await initialize();
        await vi.advanceTimersByTimeAsync(1);

        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        expect(JSON.parse(localStorage.getItem('ambiance_onboarding_invitation')!).startedAt).toBe(startedAt);
        document.querySelector<HTMLButtonElement>('.action-notification-action')!.click();
        expect(tourMocks.goToStep).toHaveBeenCalledWith(0);
        await initialize();
        await vi.advanceTimersByTimeAsync(delay);
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it('suppresses the pending or visible invitation after a manual button click', async () => {
        document.body.innerHTML += '<button id="start-onboarding-btn"></button>';
        await initialize();
        document.getElementById('start-onboarding-btn')!.click();
        await vi.advanceTimersByTimeAsync(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
        expect(tourMocks.goToStep).toHaveBeenCalledWith(0);
    });

    it('closes a visible invitation when the tour is started using the home button', async () => {
        document.body.innerHTML += '<button id="start-onboarding-btn"></button>';
        await initialize();
        await vi.advanceTimersByTimeAsync(60000);
        expect(document.querySelector('.action-notification')).not.toBeNull();
        document.getElementById('start-onboarding-btn')!.click();
        expect(document.querySelector('.action-notification')).toBeNull();
        expect(tourMocks.goToStep).toHaveBeenCalledWith(0);
    });

    it('preserves a redirected anonymous tour without offering an invitation', async () => {
        sessionStorage.setItem('ambiance_shepherd_session', JSON.stringify({
            currentStep: 0, inProgress: true, redirectPath: globalThis.location.pathname,
        }));
        await initialize();
        await vi.advanceTimersByTimeAsync(60000);
        expect(tourMocks.show).toHaveBeenCalledWith(0);
        expect(sessionStorage.getItem('ambiance_shepherd_session')).toBeNull();
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it.each(['true', '', 'invalid'])('offers without automatically starting for authentication marker %s', async marker => {
        document.documentElement.dataset.userAuthenticated = marker;
        await initialize();
        await vi.advanceTimersByTimeAsync(60000);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
        expect(tourMocks.start).not.toHaveBeenCalled();
        expect(tourMocks.show).not.toHaveBeenCalled();
    });

    it('does not resume an active tour after a reload without a redirect', async () => {
        sessionStorage.setItem('ambiance_shepherd_session', JSON.stringify({
            currentStep: 0, inProgress: true, redirectPath: null,
        }));
        await initialize();

        expect(tourMocks.show).not.toHaveBeenCalled();
        expect(tourMocks.start).not.toHaveBeenCalled();
        await vi.advanceTimersByTimeAsync(delay);
        expect(document.querySelectorAll('.action-notification')).toHaveLength(1);
    });

    it('does not invite when the feature is disabled', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true, json: async () => ({ ...context, feature_flags: { onboarding_enabled: false } }),
        }));
        await initialize();
        await vi.advanceTimersByTimeAsync(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it.each([null, { ...context, steps: {} }, { ...context, labels: null }])
    ('does not invite for malformed API context %j', async payload => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => payload }));
        await initialize();
        await vi.advanceTimersByTimeAsync(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
        expect(tourMocks.initialize).not.toHaveBeenCalled();
    });

    it('does not invite when the API is unavailable', async () => {
        vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
        await initialize();
        await vi.advanceTimersByTimeAsync(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it.each([false, true])('does not invite when the tour is unavailable or empty (%s)', async available => {
        tourMocks.available = available;
        tourMocks.steps = [];
        await initialize();
        await vi.advanceTimersByTimeAsync(60000);
        expect(document.querySelector('.action-notification')).toBeNull();
    });

    it('still offers when sessionStorage access is denied', async () => {
        vi.stubGlobal('sessionStorage', {
            getItem: () => { throw new Error('Storage denied'); },
            setItem: () => { throw new Error('Storage denied'); },
        });
        await initialize();
        await vi.advanceTimersByTimeAsync(60000);
        expect(document.querySelector('.action-notification')).not.toBeNull();
    });
});