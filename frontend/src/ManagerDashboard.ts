import { DashboardLineGraph } from '@/modules/Chart/DashboardLineGraph' ;

document.addEventListener("DOMContentLoaded", () => {
    const listIdGraphLine = [
        'evolution-user',
        'activity-user',
        'activity-errors'
    ]
    for (const id of listIdGraphLine) {
        new DashboardLineGraph(id, 'periode-chart').init();
    };
});

