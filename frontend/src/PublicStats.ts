import { DashboardLineGraph } from '@/modules/Chart/DashboardLineGraph' ;
import { DashboardBarGraph } from '@/modules/Chart/DashboardBarGraph' ;

document.addEventListener("DOMContentLoaded", () => {
    const listIdGraphLine = [
        'user-frequentation',
    ]
    for (const id of listIdGraphLine) {
        new DashboardLineGraph(id, 'periode-chart').init();
    };
    const listIdBarLine = [
        'user-average-session-duration',
    ]
    for (const id of listIdBarLine) {
        new DashboardBarGraph(id, 'periode-chart').init();
    };

});
