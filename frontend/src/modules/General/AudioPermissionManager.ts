import ModalCustom from './Modal';

/**
 * Gestionnaire des permissions audio pour iOS
 * Gère le déblocage de l'audio qui nécessite une interaction utilisateur sur iOS
 */
class AudioPermissionManager {
    private static instance: AudioPermissionManager;
    private isAudioUnlocked: boolean = false;
    private audioContext: AudioContext | null = null;
    private tempAudio: HTMLAudioElement | null = null;

    private constructor() {}

    public static getInstance(): AudioPermissionManager {
        if (!AudioPermissionManager.instance) {
            AudioPermissionManager.instance = new AudioPermissionManager();
        }
        return AudioPermissionManager.instance;
    }

    /**
     * Vérifie si l'appareil est iOS
     */
    private isIOS(): boolean {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) || 
               (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    }

    /**
     * Vérifie si l'audio est déjà débloqué
     */
    public isAudioEnabled(): boolean {
        return this.isAudioUnlocked || !this.isIOS();
    }

    /**
     * Tente de débloquer l'audio silencieusement
     */
    private async attemptUnlockAudio(): Promise<boolean> {
        try {
            // Créer un AudioContext si pas déjà fait
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
            }

            // Reprendre le contexte audio s'il est suspendu
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            // Créer et jouer un son silencieux
            if (!this.tempAudio) {
                this.tempAudio = new Audio();
                this.tempAudio.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=';
                this.tempAudio.volume = 0;
            }

            await this.tempAudio.play();
            this.isAudioUnlocked = true;
            return true;
        } catch (error) {
            console.warn('Impossible de débloquer l\'audio automatiquement:', error);
            return false;
        }
    }

    /**
     * Affiche une modal pour demander l'autorisation audio
     */
    private showAudioPermissionModal(): Promise<boolean> {
        return new Promise((resolve) => {
            const modalBody = `
                <div class="text-center">
                    <i class="fas fa-volume-up fa-3x mb-3 text-primary"></i>
                    <p class="mb-3">
                        Pour une expérience optimale, nous devons activer l'audio sur votre appareil.
                    </p>
                    <p class="text-muted small">
                        Appuyez sur "Activer l'audio" pour continuer.
                    </p>
                </div>
            `;

            const modalFooter = `
                <button type="button" class="btn btn-secondary" id="audio-permission-cancel">
                    Plus tard
                </button>
                <button type="button" class="btn btn-primary" id="audio-permission-enable">
                    <i class="fas fa-play me-2"></i>Activer l'audio
                </button>
            `;

            ModalCustom.show({
                title: "🔊 Activation de l'audio",
                body: modalBody,
                footer: modalFooter,
                width: "sm",
                callback: () => {
                    // Bouton Activer
                    const enableBtn = document.getElementById('audio-permission-enable');
                    if (enableBtn) {
                        enableBtn.addEventListener('click', async () => {
                            const success = await this.attemptUnlockAudio();
                            ModalCustom.hide();
                            resolve(success);
                        });
                    }

                    // Bouton Annuler
                    const cancelBtn = document.getElementById('audio-permission-cancel');
                    if (cancelBtn) {
                        cancelBtn.addEventListener('click', () => {
                            ModalCustom.hide();
                            resolve(false);
                        });
                    }
                }
            });
        });
    }

    /**
     * Demande l'autorisation audio si nécessaire
     */
    public async requestAudioPermission(): Promise<boolean> {
        // Si pas iOS ou déjà débloqué, retourner true

        // if (!this.isIOS() || this.isAudioUnlocked) {
        //     return true;
        // }

        // // Tenter de débloquer silencieusement d'abord
        // const silentUnlock = await this.attemptUnlockAudio();
        // if (silentUnlock) {
        //     return true;
        // }

        // Si échec, afficher la modal
        return await this.showAudioPermissionModal();
    }

    /**
     * Force la demande d'autorisation même si déjà accordée
     */
    public async forceRequestPermission(): Promise<boolean> {
        this.isAudioUnlocked = false;
        return await this.requestAudioPermission();
    }

    /**
     * Nettoie les ressources
     */
    public cleanup(): void {
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        if (this.tempAudio) {
            this.tempAudio.remove();
            this.tempAudio = null;
        }
    }

    /**
     * Méthode utilitaire pour vérifier et débloquer l'audio avant de jouer un son
     */
    public async ensureAudioEnabled(): Promise<boolean> {
        if (!this.isAudioEnabled()) {
            return await this.requestAudioPermission();
        }
        return true;
    }

    /**
     * Ajoute les événements nécessaires pour débloquer l'audio au premier clic
     */
    public addAutoUnlockListeners(): void {
        if (!this.isIOS() || this.isAudioUnlocked) {
            return;
        }

        const unlockAudio = async () => {
            if (!this.isAudioUnlocked) {
                await this.attemptUnlockAudio();
                // Retirer les listeners après le premier succès
                if (this.isAudioUnlocked) {
                    document.removeEventListener('click', unlockAudio);
                    document.removeEventListener('touchstart', unlockAudio);
                }
            }
        };

        document.addEventListener('click', unlockAudio, { passive: true });
        document.addEventListener('touchstart', unlockAudio, { passive: true });
    }
}

export default AudioPermissionManager;
