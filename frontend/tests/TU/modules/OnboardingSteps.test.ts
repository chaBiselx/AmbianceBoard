import { describe, expect, it } from 'vitest';
import { buildStepsList, getStepById, getTotalSteps, type IOnboardingApiStep } from '@/modules/OnboardingSteps';

describe('OnboardingSteps', () => {
    const steps: IOnboardingApiStep[] = [
        {
            id: 'welcome',
            selector: '#welcome',
            position: 'top',
            title: 'Welcome',
            description: 'Welcome description',
            redirect_url: '/dashboard',
        },
        {
            id: 'finish',
            selector: '#finish',
            position: 'invalid',
            description: 'Finish description',
            redirect_url: null,
        },
    ];

    it('converts backend steps and normalizes unsupported positions', () => {
        expect(buildStepsList({ steps })).toEqual([
            {
                id: 'welcome',
                selector: '#welcome',
                position: 'top',
                title: 'Welcome',
                description: 'Welcome description',
                redirectUrl: '/dashboard',
            },
            {
                id: 'finish',
                selector: '#finish',
                position: 'bottom',
                title: undefined,
                description: 'Finish description',
                redirectUrl: undefined,
            },
        ]);
    });

    it.each(['top', 'bottom', 'left', 'right'] as const)('keeps the valid "%s" position', (position) => {
        const [step] = buildStepsList({ steps: [{ ...steps[0], position }] });

        expect(step.position).toBe(position);
    });

    it('returns the number of backend steps', () => {
        expect(getTotalSteps(steps)).toBe(2);
        expect(getTotalSteps([])).toBe(0);
    });

    it('finds a step by ID in the converted format', () => {
        expect(getStepById('finish', steps)).toEqual(buildStepsList({ steps })[1]);
        expect(getStepById('missing', steps)).toBeUndefined();
    });
});