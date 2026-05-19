import Csrf from './modules/General/Csrf';

document.addEventListener('DOMContentLoaded', () => {
    new MusicLabelerPage().init();
});

interface LabelResult {
    label: string;
    confidence: number;
}

interface CategoryResult {
    category_confidence: number;
    labels: LabelResult[];
}

interface AnalyzeResponse {
    filename: string;
    bpm: number;
    duration_seconds: number;
    categories: Record<string, CategoryResult>;
    error?: string;
}

class MusicLabelerPage {
    private labelAllBtn: HTMLButtonElement | null;
    private progressCounter: HTMLElement | null;
    private progressCurrent: HTMLElement | null;
    private progressTotal: HTMLElement | null;

    constructor() {
        this.labelAllBtn = document.getElementById('label-all-btn') as HTMLButtonElement;
        this.progressCounter = document.getElementById('progress-counter');
        this.progressCurrent = document.getElementById('progress-current');
        this.progressTotal = document.getElementById('progress-total');
    }

    init(): void {
        // Afficher les labels déjà enregistrés
        this.renderExistingLabels();

        // Boutons individuels
        for (const btn of document.querySelectorAll<HTMLButtonElement>('.label-btn')) {
            btn.addEventListener('click', () => this.analyzeOne(btn));
        }

        // Bouton "Tout labeliser"
        this.labelAllBtn?.addEventListener('click', () => this.analyzeAll());
    }

    private renderExistingLabels(): void {
        for (const cell of document.querySelectorAll<HTMLTableCellElement>('.label-result[data-labels]')) {
            const raw = cell.dataset.labels;
            if (!raw) continue;
            try {
                const data: AnalyzeResponse = JSON.parse(raw);
                cell.innerHTML = this.renderLabels(data);

                // Marquer le bouton comme déjà labélisé
                const musicId = cell.dataset.musicId;
                const btn = document.querySelector<HTMLButtonElement>(`.label-btn[data-music-id="${musicId}"]`);
                if (btn) {
                    btn.innerHTML = '<i class="fas fa-check text-success"></i>';
                    btn.classList.replace('btn-outline-primary', 'btn-outline-success');
                }
            } catch (e) {
                // Ignorer les erreurs de parsing
            }
        }
    }

    private async analyzeOne(btn: HTMLButtonElement): Promise<void> {
        const musicId = btn.dataset.musicId!;
        const url = btn.dataset.url!;
        const resultCell = document.querySelector<HTMLTableCellElement>(
            `.label-result[data-music-id="${musicId}"]`
        );

        if (!resultCell) return;

        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        resultCell.innerHTML = '<span class="text-muted"><i class="fas fa-spinner fa-spin"></i> Analyse en cours…</span>';

        try {
            const csrfToken = Csrf.getToken();
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken!,
                },
            });

            const data: AnalyzeResponse = await response.json();

            if (!response.ok || data.error) {
                resultCell.innerHTML = `<span class="badge bg-danger">${data.error || 'Erreur'}</span>`;
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-tag"></i> Retry';
                return;
            }

            resultCell.innerHTML = this.renderLabels(data);
            btn.innerHTML = '<i class="fas fa-check text-success"></i>';
            btn.classList.replace('btn-outline-primary', 'btn-outline-success');
        } catch (e) {
            resultCell.innerHTML = '<span class="badge bg-danger">Erreur réseau</span>';
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-tag"></i> Retry';
        }
    }

    private async analyzeAll(): Promise<void> {
        const buttons = document.querySelectorAll<HTMLButtonElement>('.label-btn:not(:disabled)');
        if (buttons.length === 0) return;

        if (this.progressCounter && this.progressCurrent && this.progressTotal) {
            this.progressCounter.classList.remove('d-none');
            this.progressTotal.textContent = String(buttons.length);
            this.progressCurrent.textContent = '0';
        }

        this.labelAllBtn!.disabled = true;
        this.labelAllBtn!.innerHTML = '<i class="fas fa-spinner fa-spin"></i> En cours…';

        let done = 0;
        for (const btn of buttons) {
            await this.analyzeOne(btn);
            done++;
            if (this.progressCurrent) {
                this.progressCurrent.textContent = String(done);
            }
        }

        this.labelAllBtn!.innerHTML = '<i class="fas fa-check"></i> Terminé';
    }

    private renderLabels(data: AnalyzeResponse): string {
        const MLBuilder = new MusicLabelerBuilder();

        // Trier les catégories par confiance décroissante
        const sortedCategories = Object.entries(data.categories)
            .sort(([, a], [, b]) => b.category_confidence - a.category_confidence);

        // N'afficher que les catégories avec confiance > seuil
        sortedCategories
            .forEach(([catName, cat]) => {
                MLBuilder.addCategory(catName, cat.category_confidence, cat.labels);
            });

        return MLBuilder.build();
    }
}


class MusicLabelerBuilder {
    private html = '';

    public addCategory(name: string, confidence: number, labels: LabelResult[]): this {
        const catPct = (confidence * 100).toFixed(0);
        const labelsHtml = labels.map((l) => this.addLabel(l)).join('');
        this.html += `<div class="mb-1"><small class="text-muted fw-bold">${name} (${catPct}%)</small> ${labelsHtml}</div>`;
        this.html += `<hr class="my-1">`;
        return this;
    }

    public build(): string {
        return `<div>${this.html}</div>`;
    }

    private addLabel(label: LabelResult): string {
        const pct = (label.confidence * 100).toFixed(0);
        const bg = this.transformConfidenceToClass(label.confidence);
        return `<span class="badge ${bg} me-1">${label.label} (${pct}%)</span>`;
    }

    private transformConfidenceToClass(confidence: number): string {
        if (confidence >= 0.4) return 'bg-success';
        if (confidence >= 0.30) return 'bg-info';
        return 'bg-light text-dark';
    }


}
