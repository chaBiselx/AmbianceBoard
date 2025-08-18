import Chart from 'chart.js/auto';

document.addEventListener("DOMContentLoaded", () => {
    new DashboardUser().init();
});

class DashboardUser {
    private element: HTMLElement | null;

    constructor() {
        this.element = document.getElementById('evolution-user');
    }

    public init() {
        if (this.element) {
            const url = this.element.dataset.url!;
            this.fetchData(url);
            // Fetch data and initialize chart
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
        // Créer la liste complète des dates entre start_date et end_date
        const startDate = new Date(data.start_date);
        const endDate = new Date(data.end_date);
        const dateLabels: string[] = [];
        
        for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
            dateLabels.push(d.toISOString().split('T')[0]); // Format YYYY-MM-DD
        }
        
        // Créer des dictionnaires pour accès rapide
        const createdDict: { [key: string]: number } = {};
        data.users_created.forEach((item: any) => {
            createdDict[item.date] = item.count;
        });
        
        const connectedDict: { [key: string]: number } = {};
        data.users_connected.forEach((item: any) => {
            connectedDict[item.date] = item.count;
        });
        
        // Remplir les datasets avec 0 pour les jours sans activité
        const createdData = dateLabels.map(date => createdDict[date] || 0);
        const connectedData = dateLabels.map(date => connectedDict[date] || 0);
        
        // Retourner l'objet formaté pour Chart.js
        return {
            labels: dateLabels,
            datasets: [
                {
                    label: 'Utilisateurs créés',
                    data: createdData,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Connexions',
                    data: connectedData,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1,
                    fill: false
                }
            ]
        };
    }

    private renderChart(data: any) {
        // Créer un canvas pour le graphique s'il n'existe pas
        let canvas = this.element!.querySelector('canvas') as HTMLCanvasElement;
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'userEvolutionChart';
            canvas.height = 100;
            this.element!.appendChild(canvas);
        }

        const ctx = canvas.getContext('2d')!;
        
        // Créer le graphique avec Chart.js importé
        new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Évolution des utilisateurs - 6 derniers mois'
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
                            display: true,
                            text: 'Nombre d\'utilisateurs'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Mois'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }
}