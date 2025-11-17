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
     * Couleurs prédéfinies pour les datasets
     */
    private static readonly CHART_COLORS = [
        {
            border: 'rgb(75, 192, 192)',
            background: 'rgba(75, 192, 192, 0.7)'
        },
        {
            border: 'rgb(255, 99, 132)',
            background: 'rgba(255, 99, 132, 0.7)'
        },
        {
            border: 'rgb(54, 162, 235)',
            background: 'rgba(54, 162, 235, 0.7)'
        },
        {
            border: 'rgb(255, 205, 86)',
            background: 'rgba(255, 205, 86, 0.7)'
        },
        {
            border: 'rgb(153, 102, 255)',
            background: 'rgba(153, 102, 255, 0.7)'
        },
        {
            border: 'rgb(255, 159, 64)',
            background: 'rgba(255, 159, 64, 0.7)'
        }
    ];

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
        const formattedDatasets: DatasetConfig[] = datasets.map((dataset, index) => {
            // Utiliser les couleurs personnalisées ou les couleurs par défaut
            const colors = dataset.customColors || this.CHART_COLORS[index % this.CHART_COLORS.length];

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
        const formattedDatasets: DatasetConfig[] = datasets.map((dataset, index) => {
            // Utiliser les couleurs personnalisées ou les couleurs par défaut
            const colors = dataset.customColors || this.CHART_COLORS[index % this.CHART_COLORS.length];

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
     * Configuration pour le graphique d'évolution des utilisateurs
     */
    static getLineEvolution(data: LineEvolutionData, option: OptionChartConfig): ChartConfig {
        let base = {
            type: 'line',
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
     * Configuration pour le diagramme en barres verticales
     */
    static getBarChart(data: LineEvolutionData, option: OptionChartConfig): ChartConfig {
        let base = {
            type: 'bar',
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


}
