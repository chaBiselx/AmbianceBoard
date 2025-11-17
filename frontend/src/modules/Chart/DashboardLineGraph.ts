import { ChartConfigs, OptionChartConfig, LineEvolutionData } from '@/modules/Chart/ChartConfigs';
import DashboardBaseGraph from '@/modules/Chart/DashboardBaseGraph';


class DashboardLineGraph extends DashboardBaseGraph {

    constructor(id: string, id_periode_chart: string) {
        super(id, id_periode_chart, 'userEvolutionChart');
    }

    protected processChartData(labels: string[], datasets: any[]): LineEvolutionData {
        return ChartConfigs.processingDataForLineEvolution(labels, datasets);
    }

    protected renderChart(data: LineEvolutionData) {
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

export { DashboardLineGraph };