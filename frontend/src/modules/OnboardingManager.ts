import { OnboardingShepherd, IOnboardingConfig } from '@/modules/OnboardingShepherd';
import { buildStepsList } from '@/modules/OnboardingSteps';
import { IOnboardingContextResponse } from '@/modules/OnboardingManager.types';
import ConsoleCustom from '@/modules/General/ConsoleCustom';
import Notification from '@/modules/General/Notifications';
import OnboardingInvitation from '@/modules/General/OnboardingInvitation';

/**
 * Gestionnaire pour initialiser et contrôler la visite guidée Shepherd
 * Point d'entrée simple pour intégration dans General.ts
 */
export class OnboardingManager {
    private readonly shepherd: OnboardingShepherd;
    private readonly invitation = new OnboardingInvitation(30);
    private readonly storageKeySession = 'ambiance_shepherd_session';
    private isInitialized = false;
    private isInitializing = false;
    private listenersAttached = false;

    constructor() {
        this.shepherd = OnboardingShepherd.getInstance();
    }

    /**
     * Initialise la visite guidée si les conditions sont réunies
     */
    public async initialize(): Promise<void> {
        if (this.isInitializing || this.isInitialized) {
            ConsoleCustom.log('OnboardingManager initialize skipped (already running/initialized)');
            return;
        }

        this.isInitializing = true;

        try {
            // Attendre que le DOM soit complètement prêt
            await this.waitForDOMReady();

            const apiContext = await this.fetchOnboardingContext();
            if (!apiContext) {
                ConsoleCustom.warn('Onboarding context is unavailable. Tour will not start.');
                return;
            }

            if (apiContext.feature_flags.onboarding_enabled === false) {
                ConsoleCustom.log('Onboarding disabled by backend feature flag');
                return;
            }

            // TODO alony auth user afeter 01/01/2027
            const isAuthenticated = true;

            // Créer la configuration
            const config: IOnboardingConfig = {
                steps: buildStepsList({
                    steps: apiContext.steps,
                }),
                isAuthenticated,
                labels: apiContext.labels,
            };

            // Initialiser Shepherd
            this.shepherd.initialize(config);
            const tour = this.shepherd.getShepherdTour();
            if (!tour || tour.steps.length === 0) return;
            this.isInitialized = true;

            this.attachButtonListeners();
            const resumeStep = this.consumeResumeStep(tour.steps.length);
            if (resumeStep !== null) {
                this.invitation.suppress();
                await this.waitForShepherdTargets(config);
                ConsoleCustom.log(`Resuming Shepherd at step ${resumeStep}`);
                tour.show(resumeStep);
            }

            else {
                ConsoleCustom.log(`=== Starting onboarding invitation ===`);

                this.invitation.initialize(() => this.startTour());
            }

            ConsoleCustom.log('Onboarding Shepherd initialized');
        } catch (error) {
            ConsoleCustom.error('Error initializing Onboarding Shepherd:', error);
        } finally {
            this.isInitializing = false;
        }
    }

    private async fetchOnboardingContext(): Promise<IOnboardingContextResponse | null> {
        try {
            const response = await fetch('/onboarding/context', {
                method: 'GET',
                headers: {
                    Accept: 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`Unexpected onboarding context status: ${response.status}`);
            }

            const data = await response.json() as IOnboardingContextResponse;

            // Defensive fallback on malformed payload while preserving graceful behavior.
            if (!Array.isArray(data?.steps)
                || !data.steps.every(step => step && typeof step.id === 'string'
                    && typeof step.selector === 'string' && typeof step.description === 'string')
                || typeof data?.feature_flags?.onboarding_enabled !== 'boolean'
                || ![data?.labels?.next, data?.labels?.prev, data?.labels?.done].every(label => typeof label === 'string')) {
                throw new Error('Malformed onboarding context payload');
            }

            return data;
        } catch (error) {
            ConsoleCustom.warn(`Onboarding API unavailable, using local fallback: ${error}`);
            return null;
        }
    }

    /**
     * Attendre que le DOM soit complètement prêt
     */
    private async waitForDOMReady(): Promise<void> {
        if (document.readyState === 'loading') {
            await new Promise<void>(resolve => {
                document.addEventListener('DOMContentLoaded', () => resolve(), { once: true });
            });
        }
        await new Promise<void>(resolve => setTimeout(resolve, 300));
    }

    /**
     * Attache les event listeners aux boutons de la visite guidée
     */
    private attachButtonListeners(): void {
        if (this.listenersAttached) {
            return;
        }

        // Bouton de démarrage (page d'accueil)
        const startButton = document.getElementById('start-onboarding-btn');
        if (startButton) {
            startButton.addEventListener('click', () => this.startTour());
        }
        this.listenersAttached = true;
    }

    /**
     * Lance la visite guidée
     */
    private startTour(): void {
        try {
            const tour = this.shepherd.getShepherdTour();
            if (tour) {
                this.invitation.suppress();
                this.shepherd.reset();
                this.shepherd.goToStep(0);
            } else {
                ConsoleCustom.warn('Shepherd tour not initialized yet');
                Notification.createClientNotification({
                    message: 'Veuillez attendre le chargement complet de la visite guidée...',
                    type: 'info',
                });
            }
        } catch (error) {
            ConsoleCustom.error('Error starting tour:', error);
            Notification.createClientNotification({
                message: 'Impossible de lancer la visite guidée.',
                type: 'danger',
            });
        }
    }
    /**
     * Récupère le numéro d'étape à reprendre après redirection
     */
    private consumeResumeStep(stepCount: number): number | null {
        try {
            const sessionState = sessionStorage.getItem(this.storageKeySession);
            if (sessionState) {
                sessionStorage.removeItem(this.storageKeySession);
                const state = JSON.parse(sessionState);
                if (state?.inProgress === true && state.redirectPath === globalThis.location.pathname
                    && Number.isInteger(state.currentStep) && state.currentStep >= 0 && state.currentStep < stepCount) {
                    return state.currentStep;
                }
            }
        } catch {
            return null;
        }
        return null;
    }

    /**
     * Attend que tous les sélecteurs Shepherd soient présents dans le DOM
     */
    private async waitForShepherdTargets(config: IOnboardingConfig, maxAttempts = 5): Promise<void> {
        const selectors = config.steps.map((step) => step.selector);
        const uniqueSelectors = [...new Set(selectors)];

        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            const allFound = uniqueSelectors.every((selector) => document.querySelector(selector));

            if (allFound) {
                return; // Tous les éléments sont présents
            }

            // Attendre 200ms avant de réessayer
            await new Promise((resolve) => setTimeout(resolve, 200));
        }

        ConsoleCustom.warn('Some Shepherd targets not found after timeout');
    }

    /**
     * Récupère l'instance Shepherd pour accès avancé (interne)
     */
    public getShepherd(): OnboardingShepherd {
        return this.shepherd;
    }
}

/**
 * Export par défaut pour utilisation simple
 */
export default OnboardingManager;
