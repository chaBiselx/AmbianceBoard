import ConsoleCustom from '@/modules/General/ConsoleCustom';

interface TagUpdateResponse {
    status: 'success' | 'error';
    message: string;
}

/**
 * Manages dynamic add/remove of PlaylistTags via AJAX in the moderator popup.
 *
 * Expected DOM structure (rendered by popup_playlist_tag_update.html):
 *   <div id="tags-selection" data-url-update="/moderator/playlist/<uuid>/tag/">
 *     <div class="form-check-custom">
 *       <input type="checkbox" class="form-check-input d-none" id="tag_<pk>" name="playlist_tags">
 *       <label class="badge tag-badge badge-selected|badge-unselected"
 *              data-tag-id="<pk>"
 *              data-tag-label="<label-slug>">…</label>
 *     </div>
 *   </div>
 */
export class PlaylistTagManager {
    private readonly container: HTMLElement;
    private readonly updateUrl: string;

    private static readonly CSS_SELECTED = 'badge-selected';
    private static readonly CSS_UNSELECTED = 'badge-unselected';

    constructor(container: HTMLElement) {
        const updateUrl = container.dataset.urlUpdate;
        if (!updateUrl) {
            throw new Error('PlaylistTagManager: missing data-url-update attribute on container');
        }
        this.container = container;
        this.updateUrl = updateUrl;
        this.bindEvents();
    }

    /** Attach click listeners to every tag badge inside the container. */
    private bindEvents(): void {
        const badges = this.container.querySelectorAll<HTMLLabelElement>('.tag-badge');
        badges.forEach((badge) => {
            badge.addEventListener('click', (e) => this.onBadgeClick(e, badge));
        });
    }

    private async onBadgeClick(event: Event, badge: HTMLLabelElement): Promise<void> {
        event.preventDefault();

        const tagLabel = badge.dataset.tagLabel;
        const tagId = badge.dataset.tagId;

        if (!tagLabel || !tagId) {
            ConsoleCustom.warn('PlaylistTagManager: tag badge is missing data-tag-label or data-tag-id', badge);
            return;
        }

        const checkbox = this.container.querySelector<HTMLInputElement>(`#tag_${tagId}`);
        if (!checkbox) {
            ConsoleCustom.warn('PlaylistTagManager: checkbox not found for tag id', tagId);
            return;
        }

        const willBeChecked = !checkbox.checked;
        const action: 'add' | 'remove' = willBeChecked ? 'add' : 'remove';

        // Optimistic UI update
        this.setTagState(checkbox, badge, willBeChecked);

        try {
            const response = await this.postTagUpdate(tagLabel, action);

            if (response.status !== 'success') {
                // Rollback on server-side error
                this.setTagState(checkbox, badge, !willBeChecked);
                ConsoleCustom.warn('PlaylistTagManager: server error –', response.message);
            }
        } catch (error) {
            // Rollback on network error
            this.setTagState(checkbox, badge, !willBeChecked);
            ConsoleCustom.error('PlaylistTagManager: request failed', error);
        }
    }

    /** Toggle checkbox state and badge CSS classes. */
    private setTagState(checkbox: HTMLInputElement, badge: HTMLLabelElement, selected: boolean): void {
        checkbox.checked = selected;
        badge.classList.toggle(PlaylistTagManager.CSS_SELECTED, selected);
        badge.classList.toggle(PlaylistTagManager.CSS_UNSELECTED, !selected);
    }

    private async postTagUpdate(tagLabel: string, action: 'add' | 'remove'): Promise<TagUpdateResponse> {
        const csrfToken = this.getCsrfToken();

        const body = new FormData();
        body.append('playlist_tag_label', tagLabel);
        body.append('action', action);
        body.append('csrfmiddlewaretoken', csrfToken);

        const response = await fetch(this.updateUrl, {
            method: 'POST',
            body,
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return response.json() as Promise<TagUpdateResponse>;
    }

    private getCsrfToken(): string {
        // 1. Cookie (standard Django setup)
        for (const part of document.cookie.split(';')) {
            const [name, value] = part.split('=').map((s) => s.trim());
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }

        // 2. Hidden input anywhere in the page
        const input = document.querySelector<HTMLInputElement>('[name="csrfmiddlewaretoken"]');
        if (input) return input.value;

        // 3. Meta tag
        const meta = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]');
        if (meta) return meta.content;

        ConsoleCustom.warn('PlaylistTagManager: CSRF token not found');
        return '';
    }

    /**
     * Factory: finds the #tags-selection container in the current document
     * and returns a PlaylistTagManager instance, or null if not present.
     */
    static initFromDOM(): PlaylistTagManager | null {
        const container = document.getElementById('tags-selection');
        if (!container) return null;

        try {
            return new PlaylistTagManager(container);
        } catch (e) {
            ConsoleCustom.error('PlaylistTagManager.initFromDOM:', e);
            return null;
        }
    }
}
