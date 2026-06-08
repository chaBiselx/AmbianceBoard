import { IShepherdStep } from './OnboardingShepherd';

export type OnboardingLocale = 'fr' | 'en';

export type OnboardingStepPosition = 'top' | 'bottom' | 'left' | 'right';

export interface IOnboardingApiStep {
    id: string;
    selector: string;
    position?: string;
    title?: string;
    description: string;
    redirect_url?: string | null;
}


export interface IBuildStepsOptions {
    steps: IOnboardingApiStep[];
}

function normalizePosition(position?: string): OnboardingStepPosition {
    if (position === 'top' || position === 'bottom' || position === 'left' || position === 'right') {
        return position;
    }

    return 'bottom';
}

/**
 * Convertit les étapes backend en format Shepherd frontend.
 */
export function buildStepsList(options: IBuildStepsOptions): IShepherdStep[] {
    return options.steps.map((step) => ({
        id: step.id,
        selector: step.selector,
        title: step.title,
        description: step.description,
        position: normalizePosition(step.position),
        redirectUrl: step.redirect_url ?? undefined,
    }));
}

/**
 * Compte le nombre total d'étapes pour un utilisateur
 */
export function getTotalSteps(steps: IOnboardingApiStep[]): number {
    return steps.length;
}

/**
 * Récupère une étape par son ID
 */
export function getStepById(stepId: string, steps: IOnboardingApiStep[]): IShepherdStep | undefined {
    return buildStepsList({ steps }).find((step) => step.id === stepId);
}

export default {
    buildStepsList,
    getStepById,
    getTotalSteps,
};
