

import { ChartWrapper } from '@/modules/Chart/ChartWrapper';
import { LineEvolutionData } from '@/modules/Chart/ChartConfigs';
import { DataProcessor } from '@/modules/Util/DataProcessor';

abstract class DashboardBaseGraph {
    protected readonly element: HTMLElement | null;
    protected chartWrapper: ChartWrapper | null = null;
    protected readonly periodeChart: HTMLSelectElement | null;

    protected title: string = '';
    protected x_label: string = '';
    protected y_label: string = '';

    constructor(id: string, id_periode_chart: string, protected chartId: string) {
        this.element = document.getElementById(id);
        this.periodeChart = document.getElementById(id_periode_chart) as HTMLSelectElement | null;
    }

    public init() {
        if (this.element) {
            const url = this.element.dataset.url!;
            this.chartWrapper = new ChartWrapper(this.element, this.chartId);
            this.fetchData(url);
        }
    }

    protected fetchData(url: string) {
        const selectedPeriod = this.periodeChart?.value || '91';
        fetch(`${url}?period=${selectedPeriod}`)
            .then(response => response.json())
            .then(response => {
                this.title = response.title;
                this.x_label = response.x_label;
                this.y_label = response.y_label;
                this.renderChart(this.dataProcessing(response.data));
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    protected dataProcessing(data: any): LineEvolutionData {
        // Valider les données requises
        DataProcessor.validateRequiredData(data, [
            'start_date',
            'end_date',
            'data'
        ]);

        const dateLabels = DataProcessor.generateDateRange(data.start_date, data.end_date);
        let datasets = {} as { [key: string]: any };

        for (const [_, element] of Object.entries(data.data as { [key: string]: any })) {
            const dataDict = DataProcessor.createDataDictionary(element.data);
            datasets[element.key] = {
                'label': element.label,
                'data': DataProcessor.fillMissingDatas(dateLabels, dataDict)
            };
        }

        return this.processChartData(dateLabels, Object.values(datasets));
    }

    protected abstract processChartData(labels: string[], datasets: any[]): LineEvolutionData;

    protected abstract renderChart(data: LineEvolutionData): void;
}

export default DashboardBaseGraph;