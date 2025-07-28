import ModalCustom from "@/modules/General/Modal";


document.addEventListener('DOMContentLoaded', function () {
    new TiersManager().addEvent();
});

class TiersManager {
    private readonly tierSelect: HTMLSelectElement;
    private readonly expiryInput: HTMLInputElement;
    private readonly tierPreview: HTMLElement;
    private readonly previewContent: HTMLElement;
    private readonly downgradeBtn: HTMLElement;
    private readonly submitBtn: HTMLButtonElement;
    private readonly templateModalDownGradeBody: HTMLElement;
    private readonly templateModalDownGradeFooter: HTMLElement;
    private readonly tierChoices: Record<string, any>;

    constructor() {
        this.tierSelect = document.getElementById('tier_name') as HTMLSelectElement;
        this.expiryInput = document.getElementById('tier_expiry_date') as HTMLInputElement;
        this.tierPreview = document.getElementById('tier-preview') as HTMLElement;
        this.previewContent = document.getElementById('preview-content') as HTMLElement;
        this.downgradeBtn = document.getElementById('downgrade-btn') as HTMLElement;
        this.submitBtn = document.getElementById('submit-btn') as HTMLButtonElement;
        this.templateModalDownGradeBody = document.getElementById('downgradeModalBody')! as HTMLElement;
        this.templateModalDownGradeFooter = document.getElementById('downgradeModalFooter')! as HTMLElement;
        this.tierChoices = JSON.parse(document.getElementById('tier-choices-data')!.textContent!);

    }

    public addEvent() {
        this.updateTierPreview();
        this.updateExpiryDateSuggestion();


        // Événements
        this.tierSelect.addEventListener('change', () => {
            this.updateTierPreview();
            this.updateExpiryDateSuggestion();
        });

        // Modal de confirmation pour downgrade
        if (this.downgradeBtn) {
            this.downgradeBtn.addEventListener('click', () => {
                this.showModalDowngrade();
            });
        }

        // Confirmation avant soumission du formulaire
        document.getElementById('edit-tier-form')!.addEventListener('submit', (e) => {
            const selectedTier = this.tierSelect.value;
            const currentTier = '{{ user_tier.tier_name }}';

            if (selectedTier !== currentTier) {
                const tierInfo = this.tierChoices[selectedTier];
                const message = `Confirmer le changement de tier vers "${tierInfo.display_name}" ?`;

                if (!confirm(message)) {
                    e.preventDefault();
                }
            }
        });
    }

    private showModalDowngrade() {
        ModalCustom.show({
                    title: 'Confirmation de downgrade',
                    body: this.templateModalDownGradeBody.innerHTML,
                    footer: this.templateModalDownGradeFooter.innerHTML,
                    width: 'md',
                });
    }

    // Fonction pour mettre à jour l'aperçu
    private updateTierPreview() {
        const selectedTier = this.tierSelect.value;
        const tierInfo = this.tierChoices[selectedTier];

        if (tierInfo && selectedTier !== '{{ user_tier.tier_name }}') {
            const limits = tierInfo.limits;

            this.previewContent.innerHTML = `
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="text-muted small">Soundboards</div>
                        <div class="h5 mb-0">${limits.soundboard}</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="text-muted small">Playlists</div>
                        <div class="h5 mb-0">${limits.playlist}</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="text-muted small">Musiques/playlist</div>
                        <div class="h5 mb-0">${limits.music_per_playlist}</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="text-muted small">Taille max (MB)</div>
                        <div class="h5 mb-0">${limits.weight_music_mb}</div>
                    </div>
                </div>
            `;

            this.tierPreview.style.display = 'block';

            // Mise à jour du bouton selon le type de changement
            const currentTier = '{{ user_tier.tier_name }}';
            const tierHierarchy = ['STANDARD', 'PREMIUM_BASIC', 'PREMIUM_ADVANCED', 'PREMIUM_PRO'];
            const currentIndex = tierHierarchy.indexOf(currentTier);
            const newIndex = tierHierarchy.indexOf(selectedTier);

            if (newIndex > currentIndex) {
                this.submitBtn.innerHTML = '<i class="fas fa-arrow-up"></i> Upgrader le tier';
                this.submitBtn.className = 'btn btn-success';
            } else if (newIndex < currentIndex) {
                this.submitBtn.innerHTML = '<i class="fas fa-arrow-down"></i> Downgrader le tier';
                this.submitBtn.className = 'btn btn-warning';
            } else {
                this.submitBtn.innerHTML = '<i class="fas fa-save"></i> Enregistrer les modifications';
                this.submitBtn.className = 'btn btn-primary';
            }
        } else {
            this.tierPreview.style.display = 'none';
            this.submitBtn.innerHTML = '<i class="fas fa-save"></i> Enregistrer les modifications';
            this.submitBtn.className = 'btn btn-primary';
        }
    }

    // Gestion des suggestions d'expiration selon le tier
    private updateExpiryDateSuggestion() {
        const selectedTier = this.tierSelect.value;

        if (selectedTier === 'STANDARD') {
            this.expiryInput.value = '';
            this.expiryInput.disabled = true;
        } else {
            this.expiryInput.disabled = false;

            // Suggestion d'une date d'expiration dans 30 jours si pas de valeur
            if (!this.expiryInput.value) {
                const futureDate = new Date();
                futureDate.setDate(futureDate.getDate() + 30);
                this.expiryInput.value = futureDate.toISOString().split('T')[0];
            }
        }
    }


}

