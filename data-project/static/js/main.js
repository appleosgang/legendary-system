let chartInstance = null;
let currentData = [];

async function loadData() {
    updateStatus("Loading data...");

    try {
        const response = await fetch('/api/load_data');
        if (!response.ok) throw new Error('Failed to load data');

        const data = await response.json();
        currentData = data.points;
        const processMapping = data.process_mapping;

        renderChart(currentData, processMapping);
        updateStatus(`Loaded ${currentData.length} log entries.`);
    } catch (error) {
        console.error(error);
        updateStatus("Error loading data.");
    }
}

async function analyze(method) {
    if (currentData.length === 0) {
        alert("Please load data first!");
        return;
    }

    updateStatus(`Running ${method}...`);

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ method: method })
        });

        const result = await response.json();

        if (result.type === 'anomaly') {
            applyAnomalyColoring(result.labels);
        }

        updateStatus("Analysis complete.");
    } catch (error) {
        console.error(error);
        updateStatus("Analysis failed.");
    }
}

function renderChart(data, mapping) {
    const ctx = document.getElementById('logChart').getContext('2d');

    if (chartInstance) {
        chartInstance.destroy();
    }

    const plotData = data.map(d => ({ x: d.x, y: d.y }));

    chartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Log Entries',
                data: plotData,
                backgroundColor: '#3b82f6', // Default blue
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const index = context.dataIndex;
                            return currentData[index].original_log;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Hour of Day (0-24)',
                        color: '#94a3b8'
                    },
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Process Name',
                        color: '#94a3b8'
                    },
                    grid: { color: '#334155' },
                    ticks: {
                        color: '#94a3b8',
                        callback: function (value, index, values) {
                            return mapping[value] || value;
                        },
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function applyAnomalyColoring(labels) {
    // Labels: 1 = Anomaly, 0 = Normal
    const colors = labels.map(label => label === 1 ? '#ef4444' : '#3b82f6'); // Red for anomaly

    chartInstance.data.datasets[0].backgroundColor = colors;
    chartInstance.data.datasets[0].label = 'Log Entries (Red = Anomaly)';
    chartInstance.update();
}



function updateStatus(msg) {
    document.getElementById('statusMessage').textContent = msg;
}
