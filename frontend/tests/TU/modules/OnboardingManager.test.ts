import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { OnboardingManager } from '@/modules/OnboardingManager';

const onboardingMocks = vi.hoisted(() => ({
    initialize: vi.fn(),
    shouldStartTour: vi.fn(),
    start: vi.fn(),
    reset: vi.fn(),
    tourStart: vi.fn(),
    tourShow: vi.fn(),
    notify: vi.fn(),
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
            getShepherdTour: () => ({ start: onboardingMocks.tourStart, show: onboardingMocks.tourShow }),
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
        document.body.innerHTML = '<button id="start-onboarding-btn"></button><button id="restart-onboarding-btn"></button><div id="profile"></div>';
    });

    afterEach(() => {
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
    });

    it('initializes authenticated steps, starts when needed, and attaches both button actions', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => validContext() }));
        onboardingMocks.shouldStartTour.mockReturnValue(true);

        await initialize();

        expect(onboardingMocks.initialize).toHaveBeenCalledWith(expect.objectContaining({
            isAuthenticated: true,
            steps: [expect.objectContaining({ id: 'private_profile', position: 'bottom' })],
        }));
        expect(onboardingMocks.start).toHaveBeenCalledOnce();

        document.getElementById('start-onboarding-btn')!.click();
        expect(onboardingMocks.tourStart).toHaveBeenCalledOnce();
    });

    it('resumes from session state and clears the resume marker', async () => {
        const sessionStore = globalThis.sessionStorage;
        sessionStore.setItem('ambiance_shepherd_session', JSON.stringify({ currentStep: 2 }));
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => validContext() }));

        await initialize();

        expect(onboardingMocks.tourShow).toHaveBeenCalledWith(2);
        expect(sessionStore.getItem('ambiance_shepherd_session')).toBeNull();
        expect(onboardingMocks.start).not.toHaveBeenCalled();
    });
});