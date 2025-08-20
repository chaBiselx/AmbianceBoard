import { ChartWrapper } from '@/modules/Chart/ChartWrapper';
import { ChartConfigs, OptionChartConfig, LineEvolutionData} from '@/modules/Chart/ChartConfigs';
import { DataProcessor } from '@/modules/Util/DataProcessor';

document.addEventListener("DOMContentLoaded", () => {
    new DashboardLineGraph('evolution-user').init();
    new DashboardLineGraph('activity-user').init();
});

class DashboardLineGraph {
    private readonly element: HTMLElement | null;
    private chartWrapper: ChartWrapper | null = null;

    constructor(id: string) {
        this.element = document.getElementById(id);
    }

    public init() {
        if (this.element) {
            const url = this.element.dataset.url!;
            this.chartWrapper = new ChartWrapper(this.element, 'userEvolutionChart');
            this.fetchData(url);
        }
    }

    private fetchData(url: string) {

        fetch(url)
            .then(response => response.json())
            .then(data => {
                data = this.dataProcessing(data);
                this.renderChart(data);
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

        Object.entries(data.data as { [key: string]: any })
            .forEach(([_key, element]) => {
                const dataDict = DataProcessor.createDataDictionary(element.data);
                datasets[element.key] = {
                    'label': element.label,
                    'data': DataProcessor.fillMissingDatas(dateLabels, dataDict)
                };
            });

        return ChartConfigs.processingDataForLineEvolution(dateLabels, Object.values(datasets));
    }

    private renderChart(data: LineEvolutionData) {
        if (!this.chartWrapper) {
            throw new Error('ChartWrapper n\'a pas été initialisé');
        }

        const chartConfig = ChartConfigs.getLineEvolution(data,
            {
                'title': 'Évolution des utilisateurs - 6 derniers mois',
                'x': { text: 'Mois' },
                'y': { text: 'Utilisateurs' }
            } as OptionChartConfig);
        this.chartWrapper.createChart(chartConfig);
    }
}
