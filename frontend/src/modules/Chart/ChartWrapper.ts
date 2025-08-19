import Chart from 'chart.js/auto';

export interface ChartConfig {
    type: string;
    data: any;
    options?: any;
}

export class ChartWrapper {
    private chart: Chart | null = null;
    private canvas: HTMLCanvasElement;
    private container: HTMLElement;

    constructor(container: HTMLElement, canvasId: string = 'chart') {
        this.container = container;
        this.canvas = this.getOrCreateCanvas(canvasId);
    }

    /**
     * Obtient le canvas existant ou en crée un nouveau
     */
    private getOrCreateCanvas(canvasId: string): HTMLCanvasElement {
        let canvas = this.container.querySelector(`#${canvasId}`) as HTMLCanvasElement;
        
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = canvasId;
            canvas.height = 100;
            this.container.appendChild(canvas);
        }
        
        return canvas;
    }

    /**
     * Crée ou met à jour le graphique
     */
    public createChart(config: ChartConfig): Chart {
        // Détruire le graphique existant s'il y en a un
        this.destroy();

        const ctx = this.canvas.getContext('2d');
        if (!ctx) {
            throw new Error('Impossible d\'obtenir le contexte 2D du canvas');
        }

        this.chart = new Chart(ctx, {
            type: config.type,
            data: config.data,
            options: config.options
        });

        return this.chart;
    }

    /**
     * Met à jour les données du graphique
     */
    public updateData(newData: any): void {
        if (!this.chart) {
            throw new Error('Aucun graphique n\'a été créé');
        }

        this.chart.data = newData;
        this.chart.update();
    }

    /**
     * Met à jour les options du graphique
     */
    public updateOptions(newOptions: any): void {
        if (!this.chart) {
            throw new Error('Aucun graphique n\'a été créé');
        }

        this.chart.options = { ...this.chart.options, ...newOptions };
        this.chart.update();
    }

    /**
     * Redimensionne le graphique
     */
    public resize(): void {
        if (this.chart) {
            this.chart.resize();
        }
    }

    /**
     * Détruit le graphique et libère les ressources
     */
    public destroy(): void {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    /**
     * Obtient l'instance Chart.js
     */
    public getChart(): Chart | null {
        return this.chart;
    }

    /**
     * Vérifie si un graphique a été créé
     */
    public hasChart(): boolean {
        return this.chart !== null;
    }
}
