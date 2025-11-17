import { ChartConfig } from './ChartWrapper';

export type DatasetConfig = {
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
    tension?: number;
    fill?: boolean;
};

export type LineEvolutionData = {
    labels: string[];
    datasets: DatasetConfig[];
};

export type OptionChartConfig = {
    title: string | undefined;
    x: {
        text: string;
    } | undefined;
    y: {
        text: string;
    } | undefined;
};

export class ChartConfigs {

    /**
     * Couleurs de base pour les graphiques
     */
    private static readonly BASE_COLORS = [
        'rgb(75, 192, 192)',
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)',
        'rgb(153, 102, 255)',
        'rgb(255, 159, 64)',
        'rgb(201, 203, 207)'
    ];

    /**
     * Génère les couleurs pour un type de graphique donné
     * @param opacity - Opacité pour le background (0.2 pour ligne, 0.7 pour barre)
     */
    private static getChartColors(opacity: number) {
        return this.BASE_COLORS.map(color => ({
            border: color,
            background: color.replace('rgb', 'rgba').replace(')', `, ${opacity})`)
        }));
    }

    /**
     * Génère les données formatées pour un graphique d'évolution en ligne
     * @param labels - Labels pour l'axe X (dates)
     * @param datasets - Configuration des datasets avec labels et données
     * @returns Données formatées pour Chart.js
     */
    static processingDataForLineEvolution(
        labels: string[],
        datasets: Array<{ label: string; data: number[]; customColors?: { border: string; background: string } }>
    ): LineEvolutionData {
        const chartColors = this.getChartColors(0.2);
        const formattedDatasets: DatasetConfig[] = datasets.map((dataset, index) => {
            // Utiliser les couleurs personnalisées ou les couleurs par défaut
            const colors = dataset.customColors || chartColors[index % chartColors.length];

            return {
                label: dataset.label,
                data: dataset.data,
                borderColor: colors.border,
                backgroundColor: colors.background,
                tension: 0.1,
                fill: false
            };
        });

        return {
            labels: labels,
            datasets: formattedDatasets
        };
    }

    /**
     * Génère les données formatées pour un diagramme en barres verticales
     * @param labels - Labels pour l'axe X (catégories)
     * @param datasets - Configuration des datasets avec labels et données
     * @returns Données formatées pour Chart.js
     */
    static processingDataForBarChart(
        labels: string[],
        datasets: Array<{ label: string; data: number[]; customColors?: { border: string; background: string } }>
    ): LineEvolutionData {
        const chartColors = this.getChartColors(0.7);
        const formattedDatasets: DatasetConfig[] = datasets.map((dataset, index) => {
            // Utiliser les couleurs personnalisées ou les couleurs par défaut
            const colors = dataset.customColors || chartColors[index % chartColors.length];

            return {
                label: dataset.label,
                data: dataset.data,
                borderColor: colors.border,
                backgroundColor: colors.background
            };
        });

        return {
            labels: labels,
            datasets: formattedDatasets
        };
    }

    /**
     * Configuration de base pour les graphiques
     * @param chartType - Type de graphique ('line' ou 'bar')
     * @param data - Données du graphique
     * @param option - Options de configuration
     */
    private static getBaseChartConfig(
        chartType: 'line' | 'bar',
        data: LineEvolutionData,
        option: OptionChartConfig
    ): ChartConfig {
        const base = {
            type: chartType,
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: false,
                        text: ''
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: false,
                            text: ''
                        }
                    },
                    x: {
                        title: {
                            display: false,
                            text: ''
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        } as ChartConfig;
        if (option.title) {
            base.options.plugins.title.text = option.title;
            base.options.plugins.title.display = true;
        }
        if (option.x) {
            base.options.scales.x.title.text = option.x.text;
            base.options.scales.x.title.display = true;
        }
        if (option.y) {
            base.options.scales.y.title.text = option.y.text;
            base.options.scales.y.title.display = true;
        }
        return base;
    }

    /**
     * Configuration pour le graphique d'évolution en ligne
     */
    static getLineEvolution(data: LineEvolutionData, option: OptionChartConfig): ChartConfig {
        return this.getBaseChartConfig('line', data, option);
    }

    /**
     * Configuration pour le diagramme en barres verticales
     */
    static getBarChart(data: LineEvolutionData, option: OptionChartConfig): ChartConfig {
        return this.getBaseChartConfig('bar', data, option);
    }


}
