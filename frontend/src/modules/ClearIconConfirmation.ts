import ModalCustom from '@/modules/General/Modal';

export function addClearIconConfirmation(entityLabel: string) {
    const clearIconCheckbox = document.getElementById('id_clear_icon') as HTMLInputElement | null;
    if (!clearIconCheckbox) return;

    clearIconCheckbox.addEventListener('change', () => {
        if (clearIconCheckbox.checked) {
            let confirmed = false;

            ModalCustom.show({
                title: 'Confirmation',
                body: `<p>Êtes-vous sûr de vouloir supprimer l'icône ${entityLabel} ?</p>`,
                footer: `<button type="button" class="btn btn-secondary" id="clear-icon-cancel">Annuler</button>
                         <button type="button" class="btn btn-danger" id="clear-icon-confirm">Confirmer</button>`,
                width: 'sm'
            });

            const confirmButton = document.getElementById('clear-icon-confirm') as HTMLButtonElement | null;
            const cancelButton = document.getElementById('clear-icon-cancel') as HTMLButtonElement | null;

            if (confirmButton) {
                confirmButton.onclick = () => {
                    confirmed = true;
                    ModalCustom.hide();
                };
            }

            if (cancelButton) {
                cancelButton.onclick = () => {
                    ModalCustom.hide();
                };
            }

            const modalEl = ModalCustom.getMainHTMLElement();
            modalEl.addEventListener('hidden.bs.modal', () => {
                if (confirmButton) {
                    confirmButton.onclick = null;
                }
                if (cancelButton) {
                    cancelButton.onclick = null;
                }
                if (!confirmed) {
                    clearIconCheckbox.checked = false;
                }
            }, { once: true });
        }
    });
}
