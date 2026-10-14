import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { OnboardingManager } from '@/modules/OnboardingManager';

const onboardingMocks = vi.hoisted(() => ({
    initialize: vi.fn(),
    shouldStartTour: vi.fn(),
    start: vi.fn(),
    reset: vi.fn(),
    goToStep: vi.fn(),
    tourStart: vi.fn(),
    tourShow: vi.fn(),
    notify: vi.fn(),
    invitationInitialize: vi.fn(),
    invitationSuppress: vi.fn(),
    log: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
}));

vi.mock('@/modules/OnboardingShepherd', () => ({
    OnboardingShepherd: {
        getInstance: () => ({
            initialize: onboardingMocks.initialize,
            shouldStartTour: onboardingMocks.shouldStartTour,
            start: onboardingMocks.start,
            reset: onboardingMocks.reset,
            goToStep: onboardingMocks.goToStep,
            getShepherdTour: () => ({ start: onboardingMocks.tourStart, show: onboardingMocks.tourShow, steps: [{}] }),
        }),
    },
}));

vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: {
        log: onboardingMocks.log,
        warn: onboardingMocks.warn,
        error: onboardingMocks.error,
    },
}));

vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: onboardingMocks.notify } }));

vi.mock('@/modules/General/OnboardingInvitation', () => ({
    default: class {
        initialize = onboardingMocks.invitationInitialize;
        suppress = onboardingMocks.invitationSuppress;
    },
}));

const validContext = (overrides: Record<string, unknown> = {}) => ({
    locale: 'en',
    labels: { next: 'Next', prev: 'Previous', done: 'Done' },
    steps: [{ id: 'private_profile', selector: '#profile', title: 'Profile', description: 'Edit profile' }],
    feature_flags: { onboarding_enabled: true },
    ...overrides,
});

const createStorage = (): Storage => {
    const values = new Map<string, string>();
    return {
        get length() { return values.size; },
        clear: () => values.clear(),
        getItem: key => values.get(key) ?? null,
        key: index => Array.from(values.keys())[index] ?? null,
        removeItem: key => values.delete(key),
        setItem: (key, value) => values.set(key, String(value)),
    };
};

describe('OnboardingManager', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        vi.clearAllMocks();
        onboardingMocks.shouldStartTour.mockReturnValue(false);
        vi.stubGlobal('sessionStorage', createStorage());
        document.documentElement.dataset.userAuthenticated = 'true';
        document.body.innerHTML = '<button id="start-onboarding-btn"></button><button id="restart-onboarding-btn"></button><div id="profile"></div>';
    });

    afterEach(() => {
        delete document.documentElement.dataset.userAuthenticated;
        vi.useRealTimers();
        vi.unstubAllGlobals();
    });

    const initialize = async () => {
        const manager = new OnboardingManager();
        const promise = manager.initialize();
        await vi.advanceTimersByTimeAsync(1000);
        await promise;
        return manager;
    };

    it('does not initialize when the onboarding API is unavailable', async () => {
        vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));

        await initialize();

        expect(onboardingMocks.initialize).not.toHaveBeenCalled();
        expect(onboardingMocks.invitationInitialize).not.toHaveBeenCalled();
        expect(onboardingMocks.warn).toHaveBeenCalledWith(expect.stringContaining('Onboarding API unavailable'));
    });

    it('respects the backend feature flag', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            json: async () => validContext({ feature_flags: { onboarding_enabled: false } }),
        }));

        await initialize();

        expect(onboardingMocks.initialize).not.toHaveBeenCalled();
        expect(onboardingMocks.start).not.toHaveBeenCalled();
        expect(onboardingMocks.invitationInitialize).not.toHaveBeenCalled();
    });

    it('initializes authenticated steps without automatically starting an incomplete tour', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => validContext() }));
        onboardingMocks.shouldStartTour.mockReturnValue(true);

        await initialize();

        expect(onboardingMocks.initialize).toHaveBeenCalledWith(expect.objectContaining({
            isAuthenticated: true,
            steps: [expect.objectContaining({ id: 'private_profile', position: 'bottom' })],
        }));
        expect(onboardingMocks.start).not.toHaveBeenCalled();
        expect(onboardingMocks.tourShow).not.toHaveBeenCalled();
        document.getElementById('start-onboarding-btn')!.click();
        expect(onboardingMocks.goToStep).toHaveBeenCalledWith(0);
    });

    it('does not automatically start anonymous tours even with private steps', async () => {
        document.documentElement.dataset.userAuthenticated = 'false';
        onboardingMocks.shouldStartTour.mockReturnValue(true);
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => validContext() }));

        await initialize();

        expect(onboardingMocks.initialize).toHaveBeenCalledWith(expect.objectContaining({ isAuthenticated: true }));
        expect(onboardingMocks.start).not.toHaveBeenCalled();
        expect(onboardingMocks.invitationInitialize).toHaveBeenCalledOnce();
        document.getElementById('start-onboarding-btn')!.click();
        expect(onboardingMocks.goToStep).toHaveBeenCalledWith(0);
        expect(onboardingMocks.invitationSuppress).toHaveBeenCalledOnce();
    });

    it('resumes from session state and clears the resume marker', async () => {
        const sessionStore = globalThis.sessionStorage;
        sessionStore.setItem('ambiance_shepherd_session', JSON.stringify({
            currentStep: 0, inProgress: true, redirectPath: globalThis.location.pathname,
        }));
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => validContext() }));

        await initialize();

        expect(onboardingMocks.tourShow).toHaveBeenCalledWith(0);
        expect(sessionStore.getItem('ambiance_shepherd_session')).toBeNull();
        expect(onboardingMocks.start).not.toHaveBeenCalled();
        expect(onboardingMocks.invitationSuppress).toHaveBeenCalledOnce();
    });

    it.each([
        { currentStep: 0 },
        { currentStep: 0, inProgress: true, redirectPath: null },
        { currentStep: 0, inProgress: false, redirectPath: '/' },
        { currentStep: 0, inProgress: true, redirectPath: '/another-page' },
        { currentStep: -1, inProgress: true, redirectPath: '/' },
        { currentStep: 9, inProgress: true, redirectPath: '/' },
    ])('does not automatically resume without a valid active redirect: %j', async state => {
        sessionStorage.setItem('ambiance_shepherd_session', JSON.stringify(state));
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => validContext() }));

        await initialize();

        expect(onboardingMocks.tourShow).not.toHaveBeenCalled();
        expect(onboardingMocks.start).not.toHaveBeenCalled();
        expect(sessionStorage.getItem('ambiance_shepherd_session')).toBeNull();
    });

    it('consumes a redirect only once across initialization and reload', async () => {
        sessionStorage.setItem('ambiance_shepherd_session', JSON.stringify({
            currentStep: 0, inProgress: true, redirectPath: globalThis.location.pathname,
        }));
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => validContext() }));

        const manager = await initialize();
        await manager.initialize();
        await initialize();

        expect(onboardingMocks.tourShow).toHaveBeenCalledExactlyOnceWith(0);
        expect(onboardingMocks.start).not.toHaveBeenCalled();
    });

    it('restarts the tour from its first step', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => validContext() }));

        const manager = await initialize();
        manager.startTour();

        expect(onboardingMocks.reset).toHaveBeenCalledOnce();
        expect(onboardingMocks.goToStep).toHaveBeenCalledWith(0);
        expect(onboardingMocks.start).not.toHaveBeenCalled();
    });
});