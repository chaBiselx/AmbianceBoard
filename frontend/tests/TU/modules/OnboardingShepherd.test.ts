import { beforeEach, describe, expect, it, vi } from 'vitest';
import { OnboardingShepherd, type IOnboardingConfig, type IShepherdStep } from '@/modules/OnboardingShepherd';

type TestStep = {
    id: string;
    when: { show: () => void; hide: () => void };
    buttons: Array<{ action: () => void; disabled?: boolean; text: string }>;
};

const shepherdMocks = vi.hoisted(() => ({
    steps: [] as TestStep[],
    handlers: {} as Record<string, () => void>,
    currentStep: null as TestStep | null,
    start: vi.fn(),
    cancel: vi.fn(),
    next: vi.fn(),
    back: vi.fn(),
    show: vi.fn(),
    complete: vi.fn(),
    log: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
}));

vi.mock('shepherd.js', () => ({
    default: {
        Tour: class {
            steps = shepherdMocks.steps;

            addStep(step: TestStep) {
                this.steps.push(step);
            }

            on(event: string, callback: () => void) {
                shepherdMocks.handlers[event] = callback;
            }

            getCurrentStep() {
                return shepherdMocks.currentStep;
            }

            start() {
                shepherdMocks.start();
                shepherdMocks.currentStep = this.steps[0] ?? null;
            }

            cancel() {
                shepherdMocks.cancel();
                shepherdMocks.handlers.cancel?.();
            }

            next() {
                shepherdMocks.next();
            }

            back() {
                shepherdMocks.back();
            }

            show(index: number) {
                shepherdMocks.show(index);
                shepherdMocks.currentStep = this.steps[index] ?? null;
            }

            complete() {
                shepherdMocks.complete();
                shepherdMocks.handlers.complete?.();
            }
        },
    },
}));

vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: {
        log: shepherdMocks.log,
        warn: shepherdMocks.warn,
        error: shepherdMocks.error,
    },
}));

const makeConfig = (steps: IShepherdStep[] = []): IOnboardingConfig => ({
    steps,
    isAuthenticated: false,
    labels: { next: 'Next', prev: 'Previous', done: 'Done' },
});

const makeStep = (id: string, overrides: Partial<IShepherdStep> = {}): IShepherdStep => ({
    id,
    selector: `#${id}`,
    title: id,
    description: `Description for ${id}`,
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

describe('OnboardingShepherd', () => {
    let localStore: Storage;
    let sessionStore: Storage;

    beforeEach(() => {
        vi.clearAllMocks();
        shepherdMocks.steps.length = 0;
        shepherdMocks.handlers = {};
        shepherdMocks.currentStep = null;
        localStore = createStorage();
        sessionStore = createStorage();
        vi.stubGlobal('localStorage', localStore);
        vi.stubGlobal('sessionStorage', sessionStore);
        OnboardingShepherd.getInstance().reset();
        document.body.innerHTML = '';
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('filters conditional steps and creates Shepherd steps with labels and targets', () => {
        document.body.innerHTML = '<button id="visible"></button><button id="hidden"></button>';
        const service = OnboardingShepherd.getInstance();
        expect(service.getCurrentStep()).toBeNull();
        expect(service.getShepherdTour()).toBeNull();
        expect(service.getEnabledSteps()).toEqual([]);
        expect(service.shouldStartTour()).toBe(false);
        service.start();
        expect(shepherdMocks.warn).toHaveBeenCalledWith('Cannot start tour: shepherd is null');

        const config = makeConfig([
            makeStep('visible', { position: 'top' }),
            makeStep('hidden', { condition: () => false }),
        ]);
        service.initialize(config);

        expect(service.getEnabledSteps().map(step => step.id)).toEqual(['visible']);
        expect(shepherdMocks.steps).toHaveLength(1);
        expect(shepherdMocks.steps[0].buttons[0]).toMatchObject({ text: 'Previous', disabled: true });
        expect(shepherdMocks.steps[0].buttons[1].text).toBe('Done');
        shepherdMocks.steps[0].when.show();
        expect(document.getElementById('visible')!.classList.contains('onboarding-target-active')).toBe(true);
        shepherdMocks.steps[0].when.hide();
        expect(document.getElementById('visible')!.classList.contains('onboarding-target-active')).toBe(false);
    });

    it('starts the tour, saves session state, and completes from the final step', () => {
        const service = OnboardingShepherd.getInstance();
        service.initialize(makeConfig([makeStep('first'), makeStep('last')]));
        service.start();

        expect(shepherdMocks.start).toHaveBeenCalledOnce();
        expect(service.getCurrentStep()?.id).toBe('first');
        expect(JSON.parse(sessionStore.getItem('ambiance_shepherd_session')!).currentStep).toBe(0);

        shepherdMocks.steps[1].buttons[0].action();
        expect(shepherdMocks.back).toHaveBeenCalledOnce();
        shepherdMocks.steps[1].buttons[1].action();

        expect(shepherdMocks.complete).toHaveBeenCalledOnce();
        expect(JSON.parse(localStore.getItem('ambiance_shepherd_local')!).completed).toBe(true);
        expect(service.shouldStartTour()).toBe(false);
    });

    it('marks steps, navigates to a selected step, and resumes incomplete tours', () => {
        const service = OnboardingShepherd.getInstance();
        service.initialize(makeConfig([makeStep('one'), makeStep('two'), makeStep('three')]));

        expect(service.shouldStartTour()).toBe(false);
        service.markAsCompleted('one');
        expect(service.shouldStartTour()).toBe(true);
        service.goToStep(2);
        expect(shepherdMocks.show).toHaveBeenCalledWith(2);
        expect(service.getShepherdTour()).not.toBeNull();

        localStore.setItem('ambiance_shepherd_local', '{invalid');
        expect(service.shouldStartTour()).toBe(true);
    });

    it('clears persisted state on reset', () => {
        const service = OnboardingShepherd.getInstance();
        localStore.setItem('ambiance_shepherd_local', '{}');
        sessionStore.setItem('ambiance_shepherd_session', '{}');
        service.reset();

        expect(localStore.getItem('ambiance_shepherd_local')).toBeNull();
        expect(sessionStore.getItem('ambiance_shepherd_session')).toBeNull();
    });
});