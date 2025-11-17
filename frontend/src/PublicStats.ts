import { DashboardLineGraph } from '@/modules/Chart/DashboardLineGraph' ;

document.addEventListener("DOMContentLoaded", () => {
    const listIdGraphLine = [
        'user-frequentation',
    ]
    for (const id of listIdGraphLine) {
        new DashboardLineGraph(id, 'periode-chart').init();
    };
});
