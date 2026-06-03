import Shepherd from 'shepherd.js';
import 'shepherd.js/dist/css/shepherd.css';
import ConsoleCustom from './General/ConsoleCustom';

/**
 * Interface pour chaque étape du parcours Shepherd
 */
export interface IShepherdStep {
  /** ID unique pour l'étape */
  id: string;
  /** Sélecteur CSS ou data-attribute pour la cible */
  selector: string;
  /** Titre de l'étape (optionnel) */
  title?: string;
  /** Description/texte de l'étape */
  description: string;
  /** URL de redirection pour l'étape suivante (optionnel) */
  redirectUrl?: string;
  /** Condition pour afficher l'étape (optionnel) */
  condition?: () => boolean;
  /** Position du tooltip (top, bottom, left, right) */
  position?: 'top' | 'bottom' | 'left' | 'right';
  /** Classes Bootstrap personnalisées (optionnel) */
  customClass?: string;
}

/**
 * Interface pour la configuration du Shepherd
 */
export interface IOnboardingConfig {
  /** Liste des étapes à afficher */
  steps: IShepherdStep[];
  /** Indique si l'utilisateur est authentifié */
  isAuthenticated: boolean;
  /** Langue (fr, en) */
  locale: 'fr' | 'en';
  /** Labels de boutons injectés par API backend */
  labels: IOnboardingLabels;
}

export interface IOnboardingLabels {
  next: string;
  prev: string;
  done: string;
}

/**
 * Classe singleton pour gérer la visite guidée Shepherd.js
 * Gère l'état global, la persistance localStorage et les redirections
 */
export class OnboardingShepherd {
  private static instance: OnboardingShepherd | null = null;
  private shepherd: Shepherd.Tour | null = null;
  private config: IOnboardingConfig | null = null;
  private completedSteps: Set<string> = new Set();
  private storageKeyPublic = 'ambiance_shepherd_public';
  private storageKeyPrivate = 'ambiance_shepherd_private';
  private storageKeySession = 'ambiance_shepherd_session';

  /**
   * Constructeur privé pour pattern singleton
   */
  private constructor() {}

  /**
   * Récupère l'instance unique ou la crée
   */
  public static getInstance(): OnboardingShepherd {
    if (!OnboardingShepherd.instance) {
      OnboardingShepherd.instance = new OnboardingShepherd();
    }
    return OnboardingShepherd.instance;
  }

  /**
   * Initialise le Shepherd avec une configuration
   */
  public initialize(config: IOnboardingConfig): void {
    try {
      ConsoleCustom.log('Initializing OnboardingShepherd...');
      ConsoleCustom.log(`Config: authenticated=${config.isAuthenticated}, locale=${config.locale}, steps=${config.steps.length}`);

      // Prevent orphan tours creating multiple visible popups.
      if (this.shepherd) {
        this.shepherd.cancel();
        this.shepherd = null;
      }
      document
        .querySelectorAll('.onboarding-target-active')
        .forEach((el) => el.classList.remove('onboarding-target-active'));
      
      this.config = config;
      this.loadCompletedSteps();
      ConsoleCustom.log(`Loaded completed steps: ${Array.from(this.completedSteps).join(', ')}`);
      
      this.createShepherdTour(config);
      
      if (!this.shepherd) {
        ConsoleCustom.warn('Shepherd tour is null after creation');
      } else {
        ConsoleCustom.log('OnboardingShepherd initialized successfully');
      }
    } catch (error) {
      ConsoleCustom.error('Error initializing OnboardingShepherd:', error);
      throw error;
    }
  }

  /**
   * Lance la visite guidée
   */
  public start(): void {
    ConsoleCustom.log('start() called on OnboardingShepherd');
    if (this.shepherd) {
      // Avoid stacking dialogs if start is triggered repeatedly.
      if (this.shepherd.getCurrentStep()) {
        this.shepherd.cancel();
      }
      ConsoleCustom.log(`Starting tour with ${this.shepherd.steps.length} steps`);
      this.shepherd.start();
      this.saveSessionState();
    } else {
      ConsoleCustom.warn('Cannot start tour: shepherd is null');
    }
  }

  /**
   * Arrête la visite guidée
   */
  public stop(): void {
    if (this.shepherd) {
      this.shepherd.cancel();
      this.saveSessionState();
    }
  }

  /**
   * Retourne l'étape actuelle
   */
  public getCurrentStep(): Shepherd.Step | null {
    if (this.shepherd) {
      return this.shepherd.getCurrentStep();
    }
    return null;
  }

  /**
   * Marque une étape comme complétée
   */
  public markAsCompleted(stepId: string): void {
    this.completedSteps.add(stepId);
    this.saveCompletedSteps();
  }

  /**
   * Réinitialise la visite guidée (clear localStorage)
   */
  public reset(): void {
    this.completedSteps.clear();
    localStorage.removeItem(this.storageKeyPublic);
    localStorage.removeItem(this.storageKeyPrivate);
    localStorage.removeItem(this.storageKeySession);
    if (this.shepherd) {
      this.shepherd.cancel();
    }
  }

  /**
   * Navigue vers une étape et redirige si nécessaire
   */
  public goToStep(stepIndex: number): void {
    if (this.shepherd && this.config) {
      const currentStep = this.config.steps[stepIndex];
      if (currentStep && currentStep.redirectUrl) {
        // Marquer l'étape précédente comme complétée
        if (stepIndex > 0) {
          this.markAsCompleted(this.config.steps[stepIndex - 1].id);
        }
        // Sauvegarder l'état et rediriger
        this.saveSessionState(stepIndex);
        window.location.href = currentStep.redirectUrl;
      } else {
        this.shepherd.show(stepIndex);
      }
    }
  }

  /**
   * Indique si une visite guidée devrait être lancée
   */
  public shouldStartTour(): boolean {
    if (!this.config) return false;

    const storageKey = this.config.isAuthenticated ? this.storageKeyPrivate : this.storageKeyPublic;
    const savedState = localStorage.getItem(storageKey);

    if (!savedState) {
      return true; // Première visite
    }

    try {
      const state = JSON.parse(savedState);
      // Relancer si tour n'a pas été complétée entièrement
      return !state.completed && state.completed_steps.length < (this.config.isAuthenticated ? 8 : 3);
    } catch {
      return true;
    }
  }

  /**
   * Crée le tour Shepherd avec les étapes filtrées
   */
  private createShepherdTour(config: IOnboardingConfig): void {
    try {
      ConsoleCustom.log(`Creating Shepherd tour with ${config.steps.length} total steps`);
      
      const filteredSteps = this.filterSteps(config.steps, config);
      ConsoleCustom.log(`Filtered to ${filteredSteps.length} steps for user (authenticated: ${config.isAuthenticated})`);
      
      const shepherdSteps = filteredSteps.map((step, index) =>
        this.createShepherdStep(step, index, filteredSteps.length),
      );

      this.shepherd = new Shepherd.Tour({
        useModalOverlay: true,
        defaultStepOptions: {
          scrollTo: { behavior: 'smooth', block: 'center' },
          classes: `shepherd-theme-custom shepherd-${config.locale}`,
        },
      });

      ConsoleCustom.log('Shepherd.Tour instance created successfully');

      shepherdSteps.forEach((step, index) => {
        this.shepherd!.addStep(step);
        ConsoleCustom.log(`Added step ${index + 1}: ${step.id}`);
      });

      // Événement de fin de tour
      this.shepherd.on('complete', () => {
        ConsoleCustom.log('Tour completed');
        document
          .querySelectorAll('.onboarding-target-active')
          .forEach((el) => el.classList.remove('onboarding-target-active'));
        this.markAsCompleted('tour_complete');
        this.completedSteps.forEach((id) => this.markAsCompleted(id));
        this.saveCompletedSteps();
      });

      // Événement de cancel
      this.shepherd.on('cancel', () => {
        ConsoleCustom.log('Tour cancelled');
        document
          .querySelectorAll('.onboarding-target-active')
          .forEach((el) => el.classList.remove('onboarding-target-active'));
        this.saveSessionState();
      });

      ConsoleCustom.log('Shepherd tour created successfully');
    } catch (error) {
      ConsoleCustom.error('Error creating Shepherd tour:', error);
      this.shepherd = null;
    }
  }

  /**
   * Crée une étape Shepherd à partir de IShepherdStep
   */
  private createShepherdStep(
    step: IShepherdStep,
    index: number,
    total: number,
  ): Shepherd.Step.StepOptions {
    const t = this.config?.labels;
    if (!t) {
      throw new Error('Missing onboarding labels from backend context.');
    }
    const isLast = index === total - 1;

    return {
      id: step.id,
      title: step.title,
      text: step.description,
      cancelIcon: {
        enabled: true,
        label: 'Close',
      },
      attachTo: {
        element: step.selector,
        on: step.position || 'bottom',
      },
      when: {
        show: () => this.toggleTargetHighlight(step.selector, true),
        hide: () => this.toggleTargetHighlight(step.selector, false),
      },
      buttons: [
        {
          action: () => {
            if (this.shepherd && index > 0) {
              this.shepherd.back();
            }
          },
          classes: 'btn btn-secondary',
          text: t.prev,
          disabled: index === 0,
        },
        {
          action: () => {
            this.markAsCompleted(step.id);
            if (this.shepherd) {
              if (isLast) {
                this.shepherd.complete();
              } else {
                // Vérifier si l'étape suivante a une redirection
                const nextStep = this.config?.steps[index + 1];
                if (nextStep && nextStep.redirectUrl) {
                  // Sauvegarder l'état et rediriger
                  this.saveSessionState(index + 1);
                  window.location.href = nextStep.redirectUrl;
                } else {
                  this.shepherd.next();
                }
              }
            }
          },
          classes: 'btn btn-primary',
          text: isLast ? t.done : t.next,
        },
      ],
      highlightClass: 'shepherd-highlight',
      canClickTarget: false,
    };
  }

  private toggleTargetHighlight(selector: string, isActive: boolean): void {
    const target = document.querySelector(selector);
    if (!target) {
      return;
    }

    if (isActive) {
      target.classList.add('onboarding-target-active');
      return;
    }

    target.classList.remove('onboarding-target-active');
  }

  /**
   * Filtre les étapes selon la condition et l'authentification
   */
  private filterSteps(steps: IShepherdStep[], config: IOnboardingConfig): IShepherdStep[] {
    return steps.filter((step) => {
      // Vérifier la condition personnalisée
      if (step.condition && !step.condition()) {
        return false;
      }
      return true;
    });
  }

  /**
   * Charge les étapes complétées depuis localStorage
   */
  private loadCompletedSteps(): void {
    if (!this.config) return;

    const storageKey = this.config.isAuthenticated ? this.storageKeyPrivate : this.storageKeyPublic;
    const savedState = localStorage.getItem(storageKey);

    if (savedState) {
      try {
        const state = JSON.parse(savedState);
        this.completedSteps = new Set(state.completed_steps || []);
      } catch {
        this.completedSteps.clear();
      }
    }
  }

  /**
   * Sauvegarde les étapes complétées dans localStorage
   */
  private saveCompletedSteps(): void {
    if (!this.config) return;

    const storageKey = this.config.isAuthenticated ? this.storageKeyPrivate : this.storageKeyPublic;
    const state = {
      completed_steps: Array.from(this.completedSteps),
      last_visited: new Date().toISOString(),
      completed: this.completedSteps.has('tour_complete'),
    };

    localStorage.setItem(storageKey, JSON.stringify(state));
  }

  /**
   * Sauvegarde l'état de session (étape actuelle, page cible)
   */
  private saveSessionState(nextStepIndex?: number): void {
    const sessionState = {
      currentStep: nextStepIndex ?? this.shepherd?.steps.indexOf(this.shepherd.getCurrentStep()!) ?? 0,
      timestamp: new Date().toISOString(),
    };
    sessionStorage.setItem(this.storageKeySession, JSON.stringify(sessionState));
  }

  /**
   * Restaure l'état de session
   */
  private restoreSessionState(): number | null {
    const sessionState = sessionStorage.getItem(this.storageKeySession);
    if (sessionState) {
      try {
        const state = JSON.parse(sessionState);
        return state.currentStep;
      } catch {
        return null;
      }
    }
    return null;
  }

  /**
   * Génère la liste des étapes finales (publiques + privées selon auth)
   */
  public getEnabledSteps(): IShepherdStep[] {
    if (!this.config) return [];

    return this.filterSteps(this.config.steps, this.config);
  }

  /**
   * Retourne l'instance shepherd brute pour accès avancé
   */
  public getShepherdTour(): Shepherd.Tour | null {
    return this.shepherd;
  }
}

export default OnboardingShepherd;
