import { DashboardLineGraph } from '@/modules/Chart/DashboardLineGraph' ;
import ShareLinkManager from '@/modules/Event/ShareLinkManager';

function initializeHomeShareLink() {
    const sourceSelect = document.querySelector<HTMLSelectElement>('#home-share-source');
    const urlInput = document.querySelector<HTMLInputElement>('#home-share-url');
    const copyButton = document.querySelector<HTMLButtonElement>('#home-share-copy');
    const homeUrl = sourceSelect?.dataset.homeUrl;

    if (!sourceSelect || !urlInput || !copyButton || !homeUrl) {
        return;
    }

    const updateLink = () => {
        const source = sourceSelect.value;
        urlInput.value = '';
        delete copyButton.dataset.url;
        copyButton.disabled = true;

        const url = new URL(homeUrl);
        url.searchParams.set('utm_source', source);
        urlInput.value = url.toString();
        copyButton.dataset.url = urlInput.value;
        copyButton.disabled = !navigator.clipboard?.writeText;
        copyButton.title = copyButton.disabled ? 'Presse-papiers indisponible' : 'Copier le lien';
    };

    sourceSelect.addEventListener('change', updateLink);
    urlInput.addEventListener('click', () => urlInput.select());
    updateLink();
    new ShareLinkManager().addEvent();
}

document.addEventListener("DOMContentLoaded", () => {
    const listIdGraphLine = [
        'evolution-user',
        'activity-user',
        'activity-errors',
        'activity-referer',
        'activity-utm-source'
    ]
    for (const id of listIdGraphLine) {
        new DashboardLineGraph(id, 'periode-chart').init();
    };
    initializeHomeShareLink();
});

