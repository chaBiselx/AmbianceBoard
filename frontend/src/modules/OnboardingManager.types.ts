import { IOnboardingApiStep } from './OnboardingSteps';

export interface IOnboardingContextLabels {
    next: string;
    prev: string;
    done: string;
}

export interface IOnboardingFeatureFlags {
    onboarding_enabled: boolean;
}

export interface IOnboardingContextResponse {
    locale: string;
    labels: IOnboardingContextLabels;
    steps: IOnboardingApiStep[];
    feature_flags: IOnboardingFeatureFlags;
}
