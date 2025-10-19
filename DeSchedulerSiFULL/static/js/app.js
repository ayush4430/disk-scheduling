/**
 * CPU Process Scheduling Simulator - Frontend JavaScript
 * Handles user interactions, API calls, and visualization
 */

// Global variables
let ganttChart = null;
let processes = [];

// DOM elements
const processForm = document.getElementById('processForm');
const processTableBody = document.getElementById('processTableBody');
const noProcesses = document.getElementById('noProcesses');
const algorithmSelect = document.getElementById('algorithm');
const quantumInput = document.getElementById('quantumInput');
const simulateButton = document.getElementById('simulate');
const clearProcessesButton = document.getElementById('clearProcesses');
const refreshProcessesButton = document.getElementById('refreshProcesses');

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('CPU Process Scheduling Simulator initialized');
    
    // Load existing processes
    loadProcesses();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize Gantt chart
    initializeGanttChart();
});

/**
 * Set up all event listeners for the application
 */
function setupEventListeners() {
    // Process form submission
    processForm.addEventListener('submit', handleAddProcess);
    
    // Algorithm selection change
    algorithmSelect.addEventListener('change', handleAlgorithmChange);
    
    // Simulation button
    simulateButton.addEventListener('click', runSimulation);
    
    // Clear processes button
    clearProcessesButton.addEventListener('click', handleClearProcesses);
    
    // Refresh processes button
    refreshProcessesButton.addEventListener('click', loadProcesses);
}

/**
 * Handle adding a new process
 * Validates input and sends data to the backend
 */
async function handleAddProcess(event) {
    event.preventDefault();
    
    // Get form data
    const formData = {
        pid: parseInt(document.getElementById('pid').value),
        arrival_time: parseInt(document.getElementById('arrivalTime').value),
        burst_time: parseInt(document.getElementById('burstTime').value),
        priority: parseInt(document.getElementById('priority').value)
    };
    
    try {
        // Send data to backend
        const response = await fetch('/add_process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Success - clear form and reload processes
            processForm.reset();
            loadProcesses();
            showAlert('Process added successfully!', 'success');
        } else {
            // Error handling
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error adding process:', error);
        showAlert('Failed to add process. Please try again.', 'danger');
    }
}

/**
 * Load and display all processes from the backend
 */
async function loadProcesses() {
    try {
        const response = await fetch('/processes');
        const data = await response.json();
        
        if (response.ok) {
            processes = data;
            displayProcesses(processes);
        } else {
            showAlert('Failed to load processes', 'danger');
        }
    } catch (error) {
        console.error('Error loading processes:', error);
        showAlert('Failed to load processes', 'danger');
    }
}

/**
 * Display processes in the table
 */
function displayProcesses(processList) {
    if (processList.length === 0) {
        processTableBody.innerHTML = '';
        noProcesses.style.display = 'block';
        return;
    }
    
    noProcesses.style.display = 'none';
    
    processTableBody.innerHTML = processList.map(process => `
        <tr>
            <td><strong>P${process.pid}</strong></td>
            <td>${process.arrival_time}</td>
            <td>${process.burst_time}</td>
            <td>
                <span class="badge bg-secondary">${process.priority}</span>
            </td>
            <td>
                <button class="btn btn-sm btn-warning me-1" onclick="editProcess(${process.id}, ${process.arrival_time}, ${process.burst_time}, ${process.priority})">
                    Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteProcess(${process.id})">
                    Delete
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * Edit a specific process
 * Opens a prompt dialog to update process details
 */
function editProcess(processId, currentArrival, currentBurst, currentPriority) {
    // Create a simple edit dialog using prompts
    const newArrivalTime = prompt(`Edit Arrival Time (current: ${currentArrival}):`, currentArrival);
    if (newArrivalTime === null) return; // User cancelled
    
    const newBurstTime = prompt(`Edit Burst Time (current: ${currentBurst}):`, currentBurst);
    if (newBurstTime === null) return; // User cancelled
    
    const newPriority = prompt(`Edit Priority (current: ${currentPriority}, range: 1-10):`, currentPriority);
    if (newPriority === null) return; // User cancelled
    
    // Validate input
    const arrivalTime = parseInt(newArrivalTime);
    const burstTime = parseInt(newBurstTime);
    const priority = parseInt(newPriority);
    
    if (isNaN(arrivalTime) || arrivalTime < 0) {
        showAlert('Invalid arrival time. Must be non-negative.', 'danger');
        return;
    }
    if (isNaN(burstTime) || burstTime < 1) {
        showAlert('Invalid burst time. Must be positive.', 'danger');
        return;
    }
    if (isNaN(priority) || priority < 1 || priority > 10) {
        showAlert('Invalid priority. Must be between 1 and 10.', 'danger');
        return;
    }
    
    updateProcess(processId, arrivalTime, burstTime, priority);
}

/**
 * Update a process with new values
 */
async function updateProcess(processId, arrivalTime, burstTime, priority) {
    try {
        const response = await fetch(`/update_process/${processId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                arrival_time: arrivalTime,
                burst_time: burstTime,
                priority: priority
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            loadProcesses();
            showAlert('Process updated successfully!', 'success');
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error updating process:', error);
        showAlert('Failed to update process. Please try again.', 'danger');
    }
}

/**
 * Delete a specific process
 */
async function deleteProcess(processId) {
    if (!confirm('Are you sure you want to delete this process?')) {
        return;
    }
    
    try {
        const response = await fetch(`/delete_process/${processId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            loadProcesses();
            showAlert('Process deleted successfully!', 'success');
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error deleting process:', error);
        showAlert('Failed to delete process', 'danger');
    }
}

/**
 * Handle clearing all processes
 */
async function handleClearProcesses() {
    if (!confirm('Are you sure you want to clear all processes?')) {
        return;
    }
    
    try {
        const response = await fetch('/clear_processes', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            loadProcesses();
            clearGanttChart();
            clearStatistics();
            showAlert('All processes cleared!', 'success');
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error clearing processes:', error);
        showAlert('Failed to clear processes', 'danger');
    }
}

/**
 * Handle algorithm selection change
 * Show/hide time quantum input for Round Robin
 */
function handleAlgorithmChange() {
    const selectedAlgorithm = algorithmSelect.value;
    
    if (selectedAlgorithm === 'rr') {
        quantumInput.style.display = 'block';
    } else {
        quantumInput.style.display = 'none';
    }
}

/**
 * Run the scheduling simulation
 * This would typically call the backend with the selected algorithm
 */
async function runSimulation() {
    if (processes.length === 0) {
        showAlert('Please add some processes before running simulation', 'warning');
        return;
    }
    
    const algorithm = algorithmSelect.value;
    const quantum = parseInt(document.getElementById('quantum').value) || 3;
    
    // Show loading state
    simulateButton.disabled = true;
    simulateButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Running...';
    
    try {
        // For now, we'll simulate the scheduling on the frontend
        // In a real application, you might want to move this to the backend
        const result = simulateScheduling(processes, algorithm, quantum);
        
        // Update visualization and statistics
        updateGanttChart(result.timeline, algorithm);
        updateStatistics(result.statistics);
        
        showAlert(`${getAlgorithmName(algorithm)} simulation completed!`, 'success');
    } catch (error) {
        console.error('Simulation error:', error);
        showAlert('Simulation failed. Please try again.', 'danger');
    } finally {
        // Reset button state
        simulateButton.disabled = false;
        simulateButton.innerHTML = 'Run Simulation';
    }
}

/**
 * Simulate scheduling algorithms (simplified frontend implementation)
 * In a production app, this would be done on the backend
 */
function simulateScheduling(processes, algorithm, quantum = 3) {
    // Convert processes to the format expected by scheduling algorithms
    const processObjects = processes.map(p => ({
        pid: p.pid,
        arrival_time: p.arrival_time,
        burst_time: p.burst_time,
        priority: p.priority,
        remaining_time: p.burst_time
    }));
    
    let timeline = [];
    let statistics = {};
    
    switch (algorithm) {
        case 'fcfs':
            ({ timeline, statistics } = fcfsScheduling(processObjects));
            break;
        case 'sjf':
            ({ timeline, statistics } = sjfScheduling(processObjects));
            break;
        case 'rr':
            ({ timeline, statistics } = roundRobinScheduling(processObjects, quantum));
            break;
        case 'priority':
            ({ timeline, statistics } = priorityScheduling(processObjects));
            break;
        default:
            throw new Error('Unknown algorithm');
    }
    
    return { timeline, statistics };
}

/**
 * First Come First Serve (FCFS) scheduling implementation
 */
function fcfsScheduling(processes) {
    const sortedProcesses = [...processes].sort((a, b) => a.arrival_time - b.arrival_time || a.pid - b.pid);
    let currentTime = 0;
    const timeline = [];
    
    for (const process of sortedProcesses) {
        if (currentTime < process.arrival_time) {
            currentTime = process.arrival_time;
        }
        
        timeline.push({
            pid: process.pid,
            start: currentTime,
            end: currentTime + process.burst_time,
            duration: process.burst_time
        });
        
        currentTime += process.burst_time;
        
        // Calculate times for statistics
        process.completion_time = currentTime;
        process.turnaround_time = process.completion_time - process.arrival_time;
        process.waiting_time = process.turnaround_time - process.burst_time;
    }
    
    const statistics = calculateStatistics(sortedProcesses);
    return { timeline, statistics };
}

/**
 * Shortest Job First (SJF) scheduling implementation
 */
function sjfScheduling(processes) {
    const processesCopy = processes.map(p => ({ ...p }));
    const timeline = [];
    const completed = [];
    let currentTime = 0;
    
    while (completed.length < processesCopy.length) {
        // Get available processes
        const available = processesCopy.filter(p => 
            p.arrival_time <= currentTime && !completed.includes(p)
        );
        
        if (available.length > 0) {
            // Select shortest job
            const selected = available.reduce((shortest, current) => 
                current.burst_time < shortest.burst_time ? current : shortest
            );
            
            timeline.push({
                pid: selected.pid,
                start: currentTime,
                end: currentTime + selected.burst_time,
                duration: selected.burst_time
            });
            
            currentTime += selected.burst_time;
            
            selected.completion_time = currentTime;
            selected.turnaround_time = selected.completion_time - selected.arrival_time;
            selected.waiting_time = selected.turnaround_time - selected.burst_time;
            
            completed.push(selected);
        } else {
            // No process available, jump to next arrival
            const nextArrival = Math.min(...processesCopy
                .filter(p => !completed.includes(p))
                .map(p => p.arrival_time)
            );
            currentTime = nextArrival;
        }
    }
    
    const statistics = calculateStatistics(completed);
    return { timeline, statistics };
}

/**
 * Round Robin scheduling implementation
 */
function roundRobinScheduling(processes, quantum) {
    const processesCopy = processes.map(p => ({ ...p, remaining_time: p.burst_time }));
    const timeline = [];
    const queue = [];
    let currentTime = 0;
    
    // Add initially ready processes
    processesCopy.filter(p => p.arrival_time === 0).forEach(p => queue.push(p));
    
    while (queue.length > 0 || processesCopy.some(p => p.remaining_time > 0)) {
        // Add newly arrived processes
        processesCopy.filter(p => 
            p.arrival_time <= currentTime && 
            p.remaining_time > 0 && 
            !queue.includes(p)
        ).forEach(p => {
            if (!queue.includes(p)) queue.push(p);
        });
        
        if (queue.length > 0) {
            const current = queue.shift();
            const executeTime = Math.min(quantum, current.remaining_time);
            
            timeline.push({
                pid: current.pid,
                start: currentTime,
                end: currentTime + executeTime,
                duration: executeTime
            });
            
            currentTime += executeTime;
            current.remaining_time -= executeTime;
            
            if (current.remaining_time === 0) {
                current.completion_time = currentTime;
                current.turnaround_time = current.completion_time - current.arrival_time;
                current.waiting_time = current.turnaround_time - current.burst_time;
            } else {
                queue.push(current);
            }
        } else {
            // Jump to next arrival
            const nextArrival = Math.min(...processesCopy
                .filter(p => p.arrival_time > currentTime && p.remaining_time > 0)
                .map(p => p.arrival_time)
            );
            if (nextArrival !== Infinity) {
                currentTime = nextArrival;
            }
        }
    }
    
    const statistics = calculateStatistics(processesCopy);
    return { timeline, statistics };
}

/**
 * Priority scheduling implementation
 */
function priorityScheduling(processes) {
    const processesCopy = processes.map(p => ({ ...p }));
    const timeline = [];
    const completed = [];
    let currentTime = 0;
    
    while (completed.length < processesCopy.length) {
        const available = processesCopy.filter(p => 
            p.arrival_time <= currentTime && !completed.includes(p)
        );
        
        if (available.length > 0) {
            // Select highest priority (lowest number)
            const selected = available.reduce((highest, current) => 
                current.priority < highest.priority ? current : highest
            );
            
            timeline.push({
                pid: selected.pid,
                start: currentTime,
                end: currentTime + selected.burst_time,
                duration: selected.burst_time
            });
            
            currentTime += selected.burst_time;
            
            selected.completion_time = currentTime;
            selected.turnaround_time = selected.completion_time - selected.arrival_time;
            selected.waiting_time = selected.turnaround_time - selected.burst_time;
            
            completed.push(selected);
        } else {
            const nextArrival = Math.min(...processesCopy
                .filter(p => !completed.includes(p))
                .map(p => p.arrival_time)
            );
            currentTime = nextArrival;
        }
    }
    
    const statistics = calculateStatistics(completed);
    return { timeline, statistics };
}

/**
 * Calculate scheduling statistics
 */
function calculateStatistics(processes) {
    if (processes.length === 0) return {};
    
    const totalTurnaround = processes.reduce((sum, p) => sum + p.turnaround_time, 0);
    const totalWaiting = processes.reduce((sum, p) => sum + p.waiting_time, 0);
    const totalTime = Math.max(...processes.map(p => p.completion_time));
    
    return {
        avg_turnaround_time: (totalTurnaround / processes.length).toFixed(2),
        avg_waiting_time: (totalWaiting / processes.length).toFixed(2),
        avg_response_time: (totalWaiting / processes.length).toFixed(2), // Simplified
        total_time: totalTime,
        throughput: (processes.length / totalTime).toFixed(2)
    };
}

/**
 * Initialize the Gantt chart
 */
function initializeGanttChart() {
    const ctx = document.getElementById('ganttChart').getContext('2d');
    
    ganttChart = new Chart(ctx, {
        type: 'bar',
        data: {
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Process Execution Timeline'
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Time Units'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Processes'
                    }
                }
            }
        }
    });
    
    document.getElementById('noSimulation').style.display = 'block';
}

/**
 * Update the Gantt chart with simulation results
 */
function updateGanttChart(timeline, algorithm) {
    if (!timeline || timeline.length === 0) return;
    
    document.getElementById('noSimulation').style.display = 'none';
    
    // Create datasets for the Gantt chart
    const datasets = timeline.map((segment, index) => ({
        label: `P${segment.pid}`,
        data: [{
            x: [segment.start, segment.end],
            y: `P${segment.pid}`
        }],
        backgroundColor: getProcessColor(segment.pid),
        borderColor: getProcessColor(segment.pid),
        borderWidth: 1
    }));
    
    ganttChart.data.datasets = datasets;
    ganttChart.data.labels = [...new Set(timeline.map(t => `P${t.pid}`))];
    ganttChart.update();
}

/**
 * Clear the Gantt chart
 */
function clearGanttChart() {
    if (ganttChart) {
        ganttChart.data.datasets = [];
        ganttChart.update();
        document.getElementById('noSimulation').style.display = 'block';
    }
}

/**
 * Update statistics display
 */
function updateStatistics(statistics) {
    document.getElementById('avgTurnaround').textContent = statistics.avg_turnaround_time || '-';
    document.getElementById('avgWaiting').textContent = statistics.avg_waiting_time || '-';
    document.getElementById('avgResponse').textContent = statistics.avg_response_time || '-';
    document.getElementById('throughput').textContent = statistics.throughput || '-';
}

/**
 * Clear statistics display
 */
function clearStatistics() {
    document.getElementById('avgTurnaround').textContent = '-';
    document.getElementById('avgWaiting').textContent = '-';
    document.getElementById('avgResponse').textContent = '-';
    document.getElementById('throughput').textContent = '-';
}

/**
 * Get algorithm display name
 */
function getAlgorithmName(algorithm) {
    const names = {
        fcfs: 'First Come First Serve',
        sjf: 'Shortest Job First',
        rr: 'Round Robin',
        priority: 'Priority Scheduling'
    };
    return names[algorithm] || algorithm;
}

/**
 * Get color for process visualization
 */
function getProcessColor(pid) {
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
    ];
    return colors[pid % colors.length];
}

/**
 * Show alert message to user
 */
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.custom-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '1050';
    alertDiv.style.minWidth = '300px';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}