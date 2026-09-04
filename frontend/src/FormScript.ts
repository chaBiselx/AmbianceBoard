import Csrf from '@/modules/General/Csrf';
import Notification from '@/modules/General/Notifications';

const TRIGGER_WITH_SOURCE = 'ON_STEP_END';

/**
 * Éditeur de scripts d'un soundboard.
 *
 * Les listes d'étapes sont rendues côté serveur : le module ne fait que
 * déclencher les mutations puis recharger le fragment HTML correspondant.
 */
class ScriptEditor {
    private currentStepsUrl: string | null = null;

    init(): void {
        const container = document.getElementById('script-editor');
        if (!container) return;

        this.bindCreateForm(container);
        this.bindScriptListing();
    }

    private bindCreateForm(container: HTMLElement): void {
        const form = document.getElementById('script-create-form') as HTMLFormElement | null;
        const createUrl = container.dataset.urlCreate;
        if (!form || !createUrl) return;

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const response = await this.post(createUrl, new FormData(form));
            if (response) globalThis.location.reload();
        });
    }

    private bindScriptListing(): void {
        for (const item of document.querySelectorAll<HTMLElement>('#script-listing [data-script-uuid]')) {
            item.querySelector('.script-select')?.addEventListener('click', () => {
                this.loadSteps(item.dataset.urlSteps!);
            });

            item.querySelector('.script-enabled')?.addEventListener('change', (event) => {
                const body = new FormData();
                body.append('enabled', String((event.target as HTMLInputElement).checked));
                this.post(item.dataset.urlUpdate!, body);
            });

            item.querySelector('.script-delete')?.addEventListener('click', async () => {
                const response = await this.delete(item.dataset.urlDelete!, new FormData());
                if (response) globalThis.location.reload();
            });
        }
    }

    private async loadSteps(url: string): Promise<void> {
        const panel = document.getElementById('script-steps-panel');
        if (!panel) return;

        const response = await fetch(url, { method: 'GET' });
        panel.innerHTML = await response.text();
        this.currentStepsUrl = url;
        this.bindStepsPanel();
    }

    private bindStepsPanel(): void {
        const stepsContainer = document.getElementById('script-steps');
        if (!stepsContainer) return;

        this.bindStepForm(stepsContainer);
        this.bindStepActions(stepsContainer);
    }

    private bindStepForm(stepsContainer: HTMLElement): void {
        const form = document.getElementById('script-step-form') as HTMLFormElement | null;
        if (!form) return;

        const paramsByAction = JSON.parse(stepsContainer.dataset.paramsByAction ?? '{}') as Record<string, string[]>;
        const actionSelect = document.getElementById('step-action-type') as HTMLSelectElement;
        const triggerSelect = document.getElementById('step-trigger-type') as HTMLSelectElement;

        const refreshVisibility = () => {
            const requiredParams = paramsByAction[actionSelect.value] ?? [];
            for (const field of stepsContainer.querySelectorAll<HTMLElement>('.script-param')) {
                field.hidden = !requiredParams.includes(field.dataset.param ?? '');
            }
            const sourceWrapper = document.getElementById('step-source-wrapper');
            if (sourceWrapper) sourceWrapper.hidden = triggerSelect.value !== TRIGGER_WITH_SOURCE;
        };

        actionSelect.addEventListener('change', refreshVisibility);
        triggerSelect.addEventListener('change', refreshVisibility);
        refreshVisibility();

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const response = await this.post(stepsContainer.dataset.urlSave!, new FormData(form));
            if (response) await this.reloadSteps();
        });
    }

    private bindStepActions(stepsContainer: HTMLElement): void {
        for (const button of stepsContainer.querySelectorAll<HTMLButtonElement>('.step-delete')) {
            button.addEventListener('click', async () => {
                const response = await this.delete(button.dataset.urlDelete!, new FormData());
                if (response) await this.reloadSteps();
            });
        }

        for (const button of stepsContainer.querySelectorAll<HTMLButtonElement>('.step-move')) {
            button.addEventListener('click', () => {
                this.moveStep(stepsContainer, button);
            });
        }
    }

    private async moveStep(stepsContainer: HTMLElement, button: HTMLButtonElement): Promise<void> {
        const items = Array.from(stepsContainer.querySelectorAll<HTMLElement>('#script-step-list [data-step-uuid]'));
        const uuids = items.map((item) => item.dataset.stepUuid!);
        const index = items.indexOf(button.closest('[data-step-uuid]') as HTMLElement);
        const target = index + Number.parseInt(button.dataset.direction ?? '0', 10);
        if (index < 0 || target < 0 || target >= uuids.length) return;

        [uuids[index], uuids[target]] = [uuids[target], uuids[index]];

        const response = await fetch(stepsContainer.dataset.urlReorder!, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': Csrf.getToken()! },
            body: JSON.stringify({ steps: uuids }),
        });
        if (response.ok) await this.reloadSteps();
    }

    private async reloadSteps(): Promise<void> {
        if (this.currentStepsUrl) await this.loadSteps(this.currentStepsUrl);
    }

    private async delete(url: string, body: FormData): Promise<boolean> {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': Csrf.getToken()! },
            body,
        });
        if (response.ok) return true;

        const payload = await response.json().catch(() => ({}));
        Notification.createClientNotification({ message: payload.error ?? 'Error', type: 'error' });
        return false;
    }

    private async post(url: string, body: FormData): Promise<boolean> {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': Csrf.getToken()! },
            body,
        });
        if (response.ok) return true;

        const payload = await response.json().catch(() => ({}));
        Notification.createClientNotification({ message: payload.error ?? 'Error', type: 'error' });
        return false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ScriptEditor().init();
});

export default ScriptEditor;
