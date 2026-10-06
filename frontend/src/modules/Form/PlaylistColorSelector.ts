export type PlaylistColor = {
    color: string;
    colorText: string;
    typePlaylist: string;
};

type PlaylistColorList = {
    default_playlists?: PlaylistColor[];
    unique_playlists?: PlaylistColor[];
};

type PlaylistColorModalOptions = {
    title: string;
    body: string;
    footer: string;
    width: string;
    callback?: () => void;
};

export type PlaylistColorSelectorDependencies = {
    fetch: typeof fetch;
    showModal: (options: PlaylistColorModalOptions) => void;
    hideModal: () => void;
    renderPreview: (doc: Document) => void;
    log: (message: string) => void;
    error: (message: string, error?: unknown) => void;
};

export function initializePlaylistColorSelector(
    dependencies: PlaylistColorSelectorDependencies,
    doc: Document = document,
): void {
    doc.getElementById('btn-select-other-color')?.addEventListener('click', (event) => {
        const url = (event.currentTarget as HTMLElement).dataset.url;
        if (!url) return;

        void dependencies.fetch(url, { method: 'GET' })
            .then(response => response.json() as Promise<PlaylistColorList>)
            .then(playlists => showPlaylistColors(playlists, dependencies, doc))
            .catch(error => dependencies.error('Erreur lors de la requête AJAX:', error));
    });
}

function showPlaylistColors(
    playlists: PlaylistColorList,
    dependencies: PlaylistColorSelectorDependencies,
    doc: Document,
): void {
    const row = doc.createElement('div');
    row.classList.add('row');

    if (playlists.default_playlists) {
        appendSectionTitle(row, 'Playlist Defauts', doc);
        playlists.default_playlists.forEach(playlist => appendPlaylist(row, playlist, doc));
    }

    if (playlists.unique_playlists) {
        row.appendChild(doc.createElement('hr'));
        appendSectionTitle(row, 'Playlist Uniques', doc);
        playlists.unique_playlists.forEach(playlist => appendPlaylist(row, playlist, doc));
    }

    dependencies.showModal({
        title: 'Selectionner Couleur existantes',
        body: row.outerHTML,
        footer: '',
        width: 'lg',
        callback: () => {
            for (const button of doc.getElementsByClassName('btn-select-playlist-color')) {
                button.addEventListener('click', event => selectColor(event, dependencies, doc));
            }
        },
    });
}

function appendSectionTitle(row: HTMLElement, text: string, doc: Document): void {
    const title = doc.createElement('h3');
    title.classList.add('text-center');
    title.textContent = text;
    row.appendChild(title);
}

function appendPlaylist(row: HTMLElement, playlist: PlaylistColor, doc: Document): void {
    const colorColumn = doc.createElement('div');
    colorColumn.classList.add('col-4');

    const colorPreview = doc.createElement('div');
    colorPreview.innerHTML = '<small>Lorem</small>';
    colorPreview.style.backgroundColor = playlist.color;
    colorPreview.style.color = playlist.colorText;
    colorPreview.classList.add('playlist-element', 'playlist-dim-75', 'm-1');

    const typeColumn = doc.createElement('div');
    typeColumn.classList.add('col-5');
    const typeLabel = doc.createElement('small');
    typeLabel.textContent = playlist.typePlaylist;
    typeColumn.appendChild(typeLabel);

    const buttonColumn = doc.createElement('div');
    buttonColumn.classList.add('col-3');

    const button = doc.createElement('button');
    button.classList.add('btn', 'btn-primary', 'btn-select-playlist-color');
    button.type = 'button';
    button.title = 'choisir cette couleur';
    button.textContent = 'choisir';
    button.dataset.color = playlist.color;
    button.dataset.colorText = playlist.colorText;

    buttonColumn.appendChild(button);
    colorColumn.appendChild(colorPreview);
    row.append(colorColumn, typeColumn, buttonColumn);
}

function selectColor(
    event: Event,
    dependencies: PlaylistColorSelectorDependencies,
    doc: Document,
): void {
    dependencies.log('selectColor');

    const button = event.currentTarget as HTMLButtonElement;
    const colorTextInput = doc.getElementById('id_colorText') as HTMLInputElement | null;
    const colorInput = doc.getElementById('id_color') as HTMLInputElement | null;
    if (colorTextInput && colorInput) {
        colorInput.value = button.dataset.color ?? '';
        colorTextInput.value = button.dataset.colorText ?? '';
    }

    dependencies.hideModal();
    dependencies.renderPreview(doc);
}