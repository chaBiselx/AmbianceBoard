import { ChartWrapper } from '@/modules/Chart/ChartWrapper';
import { ChartConfigs, OptionChartConfig, LineEvolutionData } from '@/modules/Chart/ChartConfigs';
import { DataProcessor } from '@/modules/Util/DataProcessor';

document.addEventListener("DOMContentLoaded", () => {
    const listIdGraphLine = [
        'evolution-user',
        'activity-user',
        'activity-errors'
    ]
    for (const id of listIdGraphLine) {
        new DashboardLineGraph(id).init();
    };
});

class DashboardLineGraph {
    private readonly element: HTMLElement | null;
    private chartWrapper: ChartWrapper | null = null;
    private readonly periodeLineChart: HTMLSelectElement | null;

    private title: string = '';
    private x_label: string = '';
    private y_label: string = '';

    constructor(id: string) {
        this.element = document.getElementById(id);
        this.periodeLineChart = document.getElementById('periode-chart') as HTMLSelectElement | null;

    }

    public init() {
        if (this.element) {
            const url = this.element.dataset.url!;
            this.chartWrapper = new ChartWrapper(this.element, 'userEvolutionChart');
            this.fetchData(url);
        }
    }

    private fetchData(url: string) {
        const selectedPeriod = this.periodeLineChart?.value || '91';
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

    private dataProcessing(data: any) {
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

        return ChartConfigs.processingDataForLineEvolution(dateLabels, Object.values(datasets));
    }

    private renderChart(data: LineEvolutionData) {
        if (!this.chartWrapper) {
            throw new Error('ChartWrapper n\'a pas été initialisé');
        }

        const chartConfig = ChartConfigs.getLineEvolution(data,
            {
                'title': this.title,
                'x': { text: this.x_label },
                'y': { text: this.y_label }
            } as OptionChartConfig);
        this.chartWrapper.createChart(chartConfig);
    }
}
