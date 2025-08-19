import { ChartWrapper } from '@/modules/Chart/ChartWrapper';
import { ChartConfigs, OptionChartConfig, LineEvolutionData } from '@/modules/Chart/ChartConfigs';
import { DataProcessor } from '@/modules/Util/DataProcessor';

document.addEventListener("DOMContentLoaded", () => {
    new DashboardUser().init();
});

class DashboardUser {
    private element: HTMLElement | null;
    private chartWrapper: ChartWrapper | null = null;

    constructor() {
        this.element = document.getElementById('evolution-user');
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
            'users_created', 
            'users_connected'
        ]);

        const dateLabels = DataProcessor.generateDateRange(data.start_date, data.end_date);
        const datasets: { [key: string]: number[] } = {};
        
        Object.entries({
                'users_created': data.users_created,
                'users_connected': data.users_connected
            }
        ).forEach(([seriesName, data]) => {
            const dataDict = DataProcessor.createDataDictionary(data);
            datasets[seriesName] = DataProcessor.fillMissingDatas(dateLabels, dataDict);
        });

        return ChartConfigs.processingDataForLineEvolution(dateLabels, [
            {
                label: 'Utilisateurs créés',
                data: datasets.users_created
            },
            {
                label: 'Connexions',
                data: datasets.users_connected
            }
        ]);
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