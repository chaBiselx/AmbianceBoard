import { DashboardLineGraph } from '@/modules/Chart/DashboardLineGraph' ;

document.addEventListener("DOMContentLoaded", () => {
    const listIdGraphLine = [
        'evolution-user',
        'activity-user',
        'activity-errors',
        'activity-referer',
        'activity-utm-source'
    ]
    for (const id of listIdGraphLine) {
        new DashboardLineGraph(id, 'periode-chart').init();
    };
});

