export type PlaylistEntityActionDependencies = {
    fetch: typeof fetch;
    getCsrfToken: () => string | null;
    confirm: (message: string) => boolean;
    redirect: (url: string) => void;
    error: (message: string, error?: unknown) => void;
};

export function initializePlaylistEntityActions(
    dependencies: PlaylistEntityActionDependencies,
    doc: Document = document,
): void {
    doc.getElementById('btn-delete-playlist')?.addEventListener('click', event => {
        confirmDeletion(event, 'Êtes-vous sûr de vouloir supprimer la playlist ?', dependencies);
    });

    for (const button of doc.getElementsByClassName('btn-delete-music')) {
        button.addEventListener('click', event => {
            confirmDeletion(event, 'Êtes-vous sûr de vouloir supprimer la musique ?', dependencies);
        });
    }
}

function confirmDeletion(
    event: Event,
    message: string,
    dependencies: PlaylistEntityActionDependencies,
): void {
    const element = event.currentTarget as HTMLElement;
    const deleteUrl = element.dataset.deleteurl;
    const redirectUrl = element.dataset.redirecturl;
    if (!deleteUrl || !redirectUrl || !dependencies.confirm(message)) return;

    void dependencies.fetch(deleteUrl, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': dependencies.getCsrfToken() ?? '' },
    })
        .then(response => {
            if (response.status === 200) {
                dependencies.redirect(redirectUrl);
            } else {
                dependencies.error('Erreur lors de la suppression');
            }
        })
        .catch(error => dependencies.error('Erreur lors de la requête AJAX:', error));
}