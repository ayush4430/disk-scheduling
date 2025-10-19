/**
 * Disk Scheduling Simulator - Frontend JavaScript
 * Handles user interactions, API calls, and disk head movement visualization
 */

// Global variables
let headMovementChart = null;
let diskRequests = [];

// DOM elements
const diskRequestForm = document.getElementById('diskRequestForm');
const requestTableBody = document.getElementById('requestTableBody');
const noRequests = document.getElementById('noRequests');
const algorithmSelect = document.getElementById('algorithm');
const directionInput = document.getElementById('directionInput');
const simulateButton = document.getElementById('simulate');
const clearRequestsButton = document.getElementById('clearRequests');
const refreshRequestsButton = document.getElementById('refreshRequests');

// Algorithm descriptions
const algorithmDescriptions = {
    'fcfs': 'First Come First Serve (FCFS) - Services requests in order of arrival. Simple but may cause excessive head movement.',
    'sstf': 'Shortest Seek Time First (SSTF) - Always selects the closest request. Minimizes seek time but can cause starvation.',
    'scan': 'SCAN (Elevator) - Head moves in one direction servicing requests, then reverses. Good for fairness and reducing variance.',
    'c_scan': 'C-SCAN (Circular SCAN) - Head moves in one direction, then jumps to beginning. Provides more uniform wait times.',
    'look': 'LOOK - Similar to SCAN but only goes to the furthest request in each direction, not to disk ends.',
    'c_look': 'C-LOOK (Circular LOOK) - Similar to C-SCAN but only goes to furthest requests, not disk ends.'
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Disk Scheduling Simulator initialized');
    
    // Load existing requests
    loadDiskRequests();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize head movement chart
    initializeHeadMovementChart();
});

/**
 * Set up all event listeners for the application
 */
function setupEventListeners() {
    // Disk request form submission
    diskRequestForm.addEventListener('submit', handleAddDiskRequest);
    
    // Algorithm selection change
    algorithmSelect.addEventListener('change', handleAlgorithmChange);
    
    // Simulation button
    simulateButton.addEventListener('click', runDiskSimulation);
    
    // Clear requests button
    clearRequestsButton.addEventListener('click', handleClearRequests);
    
    // Refresh requests button
    refreshRequestsButton.addEventListener('click', loadDiskRequests);
}

/**
 * Handle adding a new disk request
 * Validates input and sends data to the backend
 */
async function handleAddDiskRequest(event) {
    event.preventDefault();
    
    // Get form data
    const formData = {
        request_id: parseInt(document.getElementById('requestId').value),
        track_number: parseInt(document.getElementById('trackNumber').value),
        arrival_time: parseInt(document.getElementById('arrivalTime').value) || 0
    };
    
    try {
        // Send data to backend
        const response = await fetch('/add_disk_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Success - clear form and reload requests
            diskRequestForm.reset();
            loadDiskRequests();
            showAlert('Disk request added successfully!', 'success');
        } else {
            // Error handling
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error adding disk request:', error);
        showAlert('Failed to add disk request. Please try again.', 'danger');
    }
}

/**
 * Load and display all disk requests from the backend
 */
async function loadDiskRequests() {
    try {
        const response = await fetch('/disk_requests');
        const data = await response.json();
        
        if (response.ok) {
            diskRequests = data;
            displayDiskRequests(diskRequests);
        } else {
            showAlert('Failed to load disk requests', 'danger');
        }
    } catch (error) {
        console.error('Error loading disk requests:', error);
        showAlert('Failed to load disk requests', 'danger');
    }
}

/**
 * Display disk requests in the table
 */
function displayDiskRequests(requestList) {
    if (requestList.length === 0) {
        requestTableBody.innerHTML = '';
        noRequests.style.display = 'block';
        return;
    }
    
    noRequests.style.display = 'none';
    
    requestTableBody.innerHTML = requestList.map(request => `
        <tr>
            <td><strong>R${request.request_id}</strong></td>
            <td>Track ${request.track_number}</td>
            <td>${request.arrival_time}</td>
            <td>
                <button class="btn btn-sm btn-warning me-1" onclick="editDiskRequest(${request.id}, ${request.track_number}, ${request.arrival_time})">
                    Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteDiskRequest(${request.id})">
                    Delete
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * Edit a specific disk request
 * Opens a prompt dialog to update request details
 */
function editDiskRequest(requestId, currentTrack, currentArrival) {
    const newTrackNumber = prompt(`Edit Track Number (current: ${currentTrack}, range: 0-199):`, currentTrack);
    if (newTrackNumber === null) return; // User cancelled
    
    const newArrivalTime = prompt(`Edit Arrival Time (current: ${currentArrival}):`, currentArrival);
    if (newArrivalTime === null) return; // User cancelled
    
    // Validate input
    const trackNumber = parseInt(newTrackNumber);
    const arrivalTime = parseInt(newArrivalTime);
    
    if (isNaN(trackNumber) || trackNumber < 0 || trackNumber > 199) {
        showAlert('Invalid track number. Must be between 0 and 199.', 'danger');
        return;
    }
    if (isNaN(arrivalTime) || arrivalTime < 0) {
        showAlert('Invalid arrival time. Must be non-negative.', 'danger');
        return;
    }
    
    updateDiskRequest(requestId, trackNumber, arrivalTime);
}

/**
 * Update a disk request with new values
 */
async function updateDiskRequest(requestId, trackNumber, arrivalTime) {
    try {
        const response = await fetch(`/update_disk_request/${requestId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                track_number: trackNumber,
                arrival_time: arrivalTime
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            loadDiskRequests();
            showAlert('Disk request updated successfully!', 'success');
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error updating disk request:', error);
        showAlert('Failed to update disk request. Please try again.', 'danger');
    }
}

/**
 * Delete a specific disk request
 */
async function deleteDiskRequest(requestId) {
    if (!confirm('Are you sure you want to delete this disk request?')) {
        return;
    }
    
    try {
        const response = await fetch(`/delete_disk_request/${requestId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            loadDiskRequests();
            showAlert('Disk request deleted successfully!', 'success');
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error deleting disk request:', error);
        showAlert('Failed to delete disk request', 'danger');
    }
}

/**
 * Handle clearing all disk requests
 */
async function handleClearRequests() {
    if (!confirm('Are you sure you want to clear all disk requests?')) {
        return;
    }
    
    try {
        const response = await fetch('/clear_disk_requests', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            loadDiskRequests();
            clearHeadMovementChart();
            clearStatistics();
            showAlert('All disk requests cleared!', 'success');
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error clearing disk requests:', error);
        showAlert('Failed to clear disk requests', 'danger');
    }
}

/**
 * Handle algorithm selection change
 * Show/hide direction input for SCAN and LOOK algorithms
 */
function handleAlgorithmChange() {
    const selectedAlgorithm = algorithmSelect.value;
    
    // Show direction input for SCAN and LOOK algorithms
    if (selectedAlgorithm === 'scan' || selectedAlgorithm === 'look') {
        directionInput.style.display = 'block';
    } else {
        directionInput.style.display = 'none';
    }
    
    // Show algorithm description
    showAlgorithmDescription(selectedAlgorithm);
}

/**
 * Show algorithm description
 */
function showAlgorithmDescription(algorithm) {
    const descriptionDiv = document.getElementById('algorithmDescription');
    const algorithmText = document.getElementById('algorithmText');
    
    if (algorithmDescriptions[algorithm]) {
        algorithmText.textContent = algorithmDescriptions[algorithm];
        descriptionDiv.style.display = 'block';
    } else {
        descriptionDiv.style.display = 'none';
    }
}

/**
 * Run the disk scheduling simulation
 */
async function runDiskSimulation() {
    if (diskRequests.length === 0) {
        showAlert('Please add some disk requests before running simulation', 'warning');
        return;
    }
    
    const algorithm = algorithmSelect.value;
    const initialHead = parseInt(document.getElementById('initialHead').value);
    const direction = document.getElementById('direction').value;
    
    // Validate initial head position
    if (isNaN(initialHead) || initialHead < 0 || initialHead > 199) {
        showAlert('Initial head position must be between 0 and 199', 'danger');
        return;
    }
    
    // Show loading state
    simulateButton.disabled = true;
    simulateButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Running...';
    
    try {
        const response = await fetch('/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                algorithm: algorithm,
                initial_head_position: initialHead,
                direction: direction,
                disk_size: 200
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Update visualization and statistics
            updateHeadMovementChart(result.head_movement, algorithm);
            updateStatistics(result.statistics);
            showAlert(`${getAlgorithmName(algorithm)} simulation completed!`, 'success');
        } else {
            showAlert(`Simulation failed: ${result.error}`, 'danger');
        }
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
 * Initialize the head movement chart
 */
function initializeHeadMovementChart() {
    const ctx = document.getElementById('headMovementChart').getContext('2d');
    
    headMovementChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Head Position',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Disk Head Movement Over Time'
                },
                legend: {
                    display: true
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
                        text: 'Track Number'
                    },
                    min: 0,
                    max: 199
                }
            }
        }
    });
    
    document.getElementById('noSimulation').style.display = 'block';
}

/**
 * Update the head movement chart with simulation results
 */
function updateHeadMovementChart(headMovement, algorithm) {
    if (!headMovement || headMovement.length === 0) return;
    
    document.getElementById('noSimulation').style.display = 'none';
    
    // Prepare data for the line chart
    const chartData = headMovement.map(movement => ({
        x: movement.time,
        y: movement.position
    }));
    
    // Update chart
    headMovementChart.data.datasets[0].data = chartData;
    headMovementChart.data.datasets[0].label = `${getAlgorithmName(algorithm)} - Head Movement`;
    headMovementChart.update();
}

/**
 * Clear the head movement chart
 */
function clearHeadMovementChart() {
    if (headMovementChart) {
        headMovementChart.data.datasets[0].data = [];
        headMovementChart.update();
        document.getElementById('noSimulation').style.display = 'block';
    }
}

/**
 * Update statistics display
 */
function updateStatistics(statistics) {
    document.getElementById('totalSeekTime').textContent = statistics.total_seek_time || '-';
    document.getElementById('avgSeekTime').textContent = statistics.avg_seek_time || '-';
    document.getElementById('totalRequests').textContent = statistics.total_requests || '-';
    document.getElementById('throughput').textContent = statistics.throughput || '-';
}

/**
 * Clear statistics display
 */
function clearStatistics() {
    document.getElementById('totalSeekTime').textContent = '-';
    document.getElementById('avgSeekTime').textContent = '-';
    document.getElementById('totalRequests').textContent = '-';
    document.getElementById('throughput').textContent = '-';
}

/**
 * Get algorithm display name
 */
function getAlgorithmName(algorithm) {
    const names = {
        fcfs: 'First Come First Serve',
        sstf: 'Shortest Seek Time First',
        scan: 'SCAN (Elevator)',
        c_scan: 'C-SCAN',
        look: 'LOOK',
        c_look: 'C-LOOK'
    };
    return names[algorithm] || algorithm.toUpperCase();
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

// Show initial algorithm description
document.addEventListener('DOMContentLoaded', function() {
    showAlgorithmDescription('fcfs');
});