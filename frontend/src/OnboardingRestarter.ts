import OnboardingManager from '@/modules/OnboardingManager';
import Notification from '@/modules/General/Notifications';
import OnboardingShepherd from '@/modules/OnboardingShepherd';

/**
 * Gestionnaire pour les boutons de lancement/relance de la visite guidée
 * Gère :
 * - #start-onboarding-btn (page d'accueil) : lance la visite
 * - #restart-onboarding-btn (page settings) : réinitialise et relance
 */
document.addEventListener('DOMContentLoaded', () => {
  // Bouton de démarrage (page d'accueil)
  const startButton = document.getElementById('start-onboarding-btn');
  if (startButton) {
    startButton.addEventListener('click', () => {
      try {
        const shepherd = OnboardingShepherd.getInstance();
        if (shepherd.getShepherdTour()) {
          shepherd.start();
        } else {
          Notification.sendNotification({
            title: 'En cours de chargement',
            body: 'Veuillez attendre le chargement complet de la visite guidée...',
            type: 'info',
          });
        }
      } catch (error) {
        Notification.sendNotification({
          title: 'Erreur',
          body: 'Impossible de lancer la visite guidée.',
          type: 'error',
        });
      }
    });
  }

  // Bouton de relance (page settings)
  const restartButton = document.getElementById('restart-onboarding-btn');
  if (restartButton) {
    restartButton.addEventListener('click', () => {
      try {
        const manager = new OnboardingManager();
        manager.restartTour();
      } catch (error) {
        Notification.sendNotification({
          title: 'Erreur',
          body: 'Impossible de relancer la visite guidée. Veuillez rafraîchir la page.',
          type: 'error',
        });
      }
    });
  }
});
