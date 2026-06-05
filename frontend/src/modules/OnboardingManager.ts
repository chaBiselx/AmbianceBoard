import { OnboardingShepherd, IOnboardingConfig } from './OnboardingShepherd';
import {
    buildStepsList,
    IOnboardingApiStep,
 } from './OnboardingSteps';
import { IOnboardingContextResponse } from './OnboardingManager.types';
import ConsoleCustom from './General/ConsoleCustom';
import Notification from './General/Notifications';

/**
 * Gestionnaire pour initialiser et contrôler la visite guidée Shepherd
 * Point d'entrée simple pour intégration dans General.ts
 */
export class OnboardingManager {
    private readonly shepherd: OnboardingShepherd;
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

            const isAuthenticated = this.isAuthenticatedFromSteps(apiContext.steps);

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
            this.isInitialized = true;

            // Attendre que le DOM soit prêt (tous les data-shepherd attrs présents)
            await this.waitForShepherdTargets(config);

            // Vérifier si on doit relancer la visite
            const resumeStep = this.getResumeStep();
            if (resumeStep !== null) {
                // On reprend depuis une redirection
                ConsoleCustom.log(`Resuming Shepherd at step ${resumeStep}`);
                this.shepherd.getShepherdTour()?.show(resumeStep);
                this.clearResumeStep();
            } else if (this.shepherd.shouldStartTour()) {
                // Première visite
                this.shepherd.start();
            }

            // Attacher les event listeners des boutons
            this.attachButtonListeners();

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
            if (!data || !data.steps || !data.feature_flags) {
                throw new Error('Malformed onboarding context payload');
            }

            return data;
        } catch (error) {
            ConsoleCustom.warn(`Onboarding API unavailable, using local fallback: ${error}`);
            return null;
        }
    }

    private isAuthenticatedFromSteps(steps: IOnboardingApiStep[]): boolean {
        // Private step IDs are only present for authenticated users in backend payload.
        return steps.some((step) => step.id.startsWith('private_'));
    }

    /**
     * Attendre que le DOM soit complètement prêt
     */
    private async waitForDOMReady(): Promise<void> {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    // Attendre 1s supplémentaires pour que tous les scripts se chargent
                    ConsoleCustom.log('DOMContentLoaded fired, waiting for all scripts...');
                    setTimeout(() => {
                        ConsoleCustom.log('Ready to initialize Onboarding');
                        resolve();
                    }, 1000);
                }, { once: true });
            } else {
                // DOM est déjà prêt, attendre un bit pour que les scripts se chargent
                ConsoleCustom.log('DOM already ready, waiting for scripts...');
                setTimeout(() => {
                    ConsoleCustom.log('Ready to initialize Onboarding');
                    resolve();
                }, 1000);
            }
        });
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

        // Bouton de relance (page settings)
        const restartButton = document.getElementById('restart-onboarding-btn');
        if (restartButton) {
            restartButton.addEventListener('click', () => this.restartTour());
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
                tour.start();
            } else {
                ConsoleCustom.warn('Shepherd tour not initialized yet');
                Notification.createClientNotification({
                    title: 'En cours de chargement',
                    body: 'Veuillez attendre le chargement complet de la visite guidée...',
                    type: 'info',
                });
            }
        } catch (error) {
            ConsoleCustom.error('Error starting tour:', error);
            Notification.createClientNotification({
                title: 'Erreur',
                body: 'Impossible de lancer la visite guidée.',
                type: 'error',
            });
        }
    }

    /**
     * Redémarrer la visite guidée (depuis les settings utilisateur)
     */
    public restartTour(): void {
        if (!this.isInitialized) return;

        this.shepherd.reset();
        // Recharger pour relancer la visite
        globalThis.location.reload();
    }

    /**
     * Récupère le numéro d'étape à reprendre après redirection
     */
    private getResumeStep(): number | null {
        const sessionState = sessionStorage.getItem(this.storageKeySession);
        if (sessionState) {
            try {
                const state = JSON.parse(sessionState);
                return state.currentStep ?? null;
            } catch {
                return null;
            }
        }
        return null;
    }

    /**
     * Efface l'état de redirection
     */
    private clearResumeStep(): void {
        sessionStorage.removeItem(this.storageKeySession);
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
