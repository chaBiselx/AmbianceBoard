import Notification from '@/modules/General/Notifications';
import * as bootstrap from 'bootstrap';
import ConsoleCustom from "@/modules/General/ConsoleCustom";



class  IOSAudioPopup {
    private popup: HTMLDivElement | null = null;
    private audio: HTMLAudioElement | null = null;
    private isShown: boolean = false;

    constructor() {
        // Vérifier si c'est iOS ou Safari
        if (this.isIOSOrSafari()) {
            this.createPopup();
        }
    }

    public addEvent() {
        if (this.isIOSOrSafari() && !this.isShown) {
            this.showPopup();
        }
    }

    private isIOSOrSafari(): boolean {
        const userAgent = navigator.userAgent;
        const isIOS = /iPad|iPhone|iPod/.test(userAgent) || 
                     (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
        const isSafari = /Safari/.test(userAgent) && !/Chrome/.test(userAgent);
        
        return isIOS || isSafari;
    }

    private createPopup() {
        // Créer le conteneur principal du popup
        this.popup = document.createElement('div');
        this.popup.className = 'modal fade';
        this.popup.id = 'iosAudioPopup';
        this.popup.setAttribute('tabindex', '-1');
        this.popup.setAttribute('aria-labelledby', 'iosAudioPopupLabel');
        this.popup.setAttribute('aria-hidden', 'true');
        this.popup.setAttribute('data-bs-backdrop', 'static');
        this.popup.setAttribute('data-bs-keyboard', 'false');

        // Créer le contenu du popup
        this.popup.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="iosAudioPopupLabel">
                            <i class="fas fa-volume-up me-2"></i>Activation Audio
                        </h5>
                    </div>
                    <div class="modal-body text-center">
                        <p class="mb-4">
                            <i class="fas fa-info-circle text-info me-2"></i>
                            Pour une meilleure expérience sur votre appareil, veuillez activer l'audio.
                        </p>
                        <audio id="iosThunderAudio" preload="auto" style="width: 100%; margin-bottom: 20px;">
                            <source src="/static/sound/thunder-test-ios.mp3" type="audio/mpeg">
                            Votre navigateur ne supporte pas l'élément audio.
                        </audio>
                        <button type="button" class="btn btn-primary btn-lg" id="startAudioBtn">
                            <i class="fas fa-play me-2"></i>Démarrer l'audio
                        </button>
                    </div>
                    <div class="modal-footer justify-content-center">
                        <small class="text-muted">
                            <i class="fab fa-safari me-1"></i>Optimisé pour iOS/Safari
                        </small>
                    </div>
                </div>
            </div>
        `;

        // Ajouter le popup au DOM
        document.body.appendChild(this.popup);

        // Récupérer les éléments audio et bouton
        this.audio = document.getElementById('iosThunderAudio') as HTMLAudioElement;
        const startButton = document.getElementById('startAudioBtn') as HTMLButtonElement;

        // Ajouter l'événement au bouton
        if (startButton && this.audio) {
            startButton.addEventListener('click', this.handleAudioStart.bind(this));
        }
    }

    private showPopup() {
        if (this.popup && !this.isShown) {
            const modal = new bootstrap.Modal(this.popup);
            modal.show();
            this.isShown = true;
        }
    }

    private handleAudioStart() {
        if (this.audio) {
            this.audio.play()
                .then(() => {
                    ConsoleCustom.log('Audio started successfully on iOS/Safari');
                    this.hidePopup();
                    Notification.createClientNotification({ 
                        message: 'Audio activé avec succès !', 
                        type: 'success' 
                    });
                })
                .catch((error) => {
                    ConsoleCustom.error('Error starting audio on iOS/Safari:', error);
                    Notification.createClientNotification({ 
                        message: 'Erreur lors de l\'activation audio', 
                        type: 'error' 
                    });
                });
        }
    }

    private hidePopup() {
        if (this.popup) {
            const modal = bootstrap.Modal.getInstance(this.popup);
            if (modal) {
                modal.hide();
            }
        }
    }
}

export default IOSAudioPopup;