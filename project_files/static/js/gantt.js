// gantt.js

// Beispiel-Daten (können durch die API-Antwort ersetzt werden)
const ganttData = {
    tasks: [
        {
            id: "1",
            name: "Projektphase 1",
            start: "2023-10-01",
            end: "2023-10-15",
            progress: 50,
            dependencies: ""
        },
        {
            id: "2",
            name: "Aktivität 1",
            start: "2023-10-02",
            end: "2023-10-05",
            progress: 80,
            dependencies: "1"
        },
        {
            id: "3",
            name: "Aktivität 2",
            start: "2023-10-06",
            end: "2023-10-10",
            progress: 30,
            dependencies: "2"
        },
        {
            id: "4",
            name: "Meilenstein 1",
            start: "2023-10-10",
            end: "2023-10-10",
            progress: 0,
            dependencies: "3"
        }
    ]
};

// Funktion zur Erstellung des Gantt-Diagramms
function createGanttChart(data) {
    // Transformiere die Daten in das von Frappe Gantt erwartete Format
    const tasks = data.tasks.map(task => ({
        id: task.id,
        name: task.name,
        start: task.start,
        end: task.end,
        progress: task.progress,
        dependencies: task.dependencies
    }));

    // Initialisiere das Gantt-Diagramm
    const gantt = new Gantt("#gantt", tasks, {
        on_click: function (task) {
            console.log("Task angeklickt:", task);
        },
        on_date_change: function (task, start, end) {
            console.log("Datum geändert:", task, start, end);
        },
        on_progress_change: function (task, progress) {
            console.log("Fortschritt geändert:", task, progress);
        },
        on_view_change: function (mode) {
            console.log("Ansicht geändert:", mode);
        }
    });
}

// Erstelle das Gantt-Diagramm mit den Beispiel-Daten
createGanttChart(ganttData);