
document.addEventListener('DOMContentLoaded', function () {
    new ListTiersManager().addEvent();
});

class ListTiersManager {
    selectAll: HTMLInputElement;
    userCheckboxes: NodeListOf<HTMLInputElement>;
    bulkActionBtn: HTMLButtonElement;
    actionSelect: HTMLSelectElement;
    extendDaysInput: HTMLInputElement;
    bulkActionForm: HTMLFormElement;

    constructor() {
        this.selectAll = document.getElementById('select-all')! as HTMLInputElement;
        this.userCheckboxes = document.querySelectorAll('.user-checkbox');
        this.bulkActionBtn = document.getElementById('bulk-action-btn')! as HTMLButtonElement;
        this.actionSelect = document.querySelector('select[name="action"]')! as HTMLSelectElement;
        this.extendDaysInput = document.getElementById('extend-days-input')! as HTMLInputElement;
        this.bulkActionForm = document.getElementById('bulk-action-form')! as HTMLFormElement;
    }

    addEvent() {

        this.selectAll.addEventListener('change', this.toggleSelectAll.bind(this));
        // Mise à jour du bouton d'action en lot
        this.userCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', this.updateBulkActionButton.bind(this));
        });

        // Afficher/masquer le champ jours selon l'action
        this.actionSelect.addEventListener('change', () => {
            if (this.actionSelect.value === 'extend_subscription') {
                this.extendDaysInput.style.display = 'inline-block';
                this.extendDaysInput.required = true;
            } else {
                this.extendDaysInput.style.display = 'none';
                this.extendDaysInput.required = false;
            }
            this.updateBulkActionButton();
        });

        this.bulkActionFormSubmit()
    }

    private toggleSelectAll() {
        const isChecked = this.selectAll.checked;
        this.userCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        this.updateBulkActionButton();
    }



    private updateBulkActionButton() {
        const selectedUsers = Array.from(this.userCheckboxes).filter(cb => cb.checked);
        this.bulkActionBtn.disabled = selectedUsers.length === 0 || !this.actionSelect.value;
    }

    private bulkActionFormSubmit() {
        this.bulkActionForm.addEventListener('submit', (e) => {
            const selectedUsers = Array.from(this.userCheckboxes).filter(cb => cb.checked);
            const action = this.actionSelect.value;

            if (selectedUsers.length === 0) {
                e.preventDefault();
                alert('Veuillez sélectionner au moins un utilisateur.');
                return;
            }

            if (!action) {
                e.preventDefault();
                alert('Veuillez sélectionner une action.');
                return;
            }

            // Ajouter les IDs des utilisateurs sélectionnés au formulaire
            // Supprimer les anciens inputs cachés s'ils existent
            const existingInputs = this.bulkActionForm.querySelectorAll('input[name="user_ids"]');
            existingInputs.forEach(input => input.remove());

            // Ajouter un input caché pour chaque utilisateur sélectionné
            selectedUsers.forEach(checkbox => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'user_ids';
                input.value = checkbox.value;
                this.bulkActionForm.appendChild(input);
            });

            const actionText = this.actionSelect.options[this.actionSelect.selectedIndex].text;
            if (!confirm(`Êtes-vous sûr de vouloir exécuter "${actionText}" sur ${selectedUsers.length} utilisateur(s) ?`)) {
                e.preventDefault();
            }
        });
    }

}

