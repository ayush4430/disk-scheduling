"""
CPU Scheduling Algorithms Implementation
Contains implementations of various scheduling algorithms for the simulator.

This module provides the core scheduling logic for:
- First Come First Serve (FCFS)
- Shortest Job First (SJF)
- Round Robin (RR)
- Priority Scheduling
"""

class Process:
    """
    Process class to represent a single process in the system.
    Contains all necessary information for scheduling simulation.
    """
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time  # For preemptive algorithms
        self.priority = priority
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = -1  # -1 indicates not started yet
        self.start_time = -1

def first_come_first_serve(processes):
    """
    First Come First Serve (FCFS) Scheduling Algorithm
    
    Non-preemptive algorithm where processes are executed in the order they arrive.
    Simple but can cause convoy effect with long processes.
    
    Args:
        processes: List of Process objects
    
    Returns:
        Tuple containing (execution_timeline, statistics)
    """
    if not processes:
        return [], {}
    
    # Sort processes by arrival time, then by PID for deterministic results
    processes_sorted = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
    
    current_time = 0
    execution_timeline = []
    
    for process in processes_sorted:
        # If CPU is idle, advance time to process arrival
        if current_time < process.arrival_time:
            current_time = process.arrival_time
        
        # Set start time and response time (first time process gets CPU)
        process.start_time = current_time
        process.response_time = current_time - process.arrival_time
        
        # Execute the process completely
        execution_timeline.append({
            'pid': process.pid,
            'start': current_time,
            'end': current_time + process.burst_time,
            'duration': process.burst_time
        })
        
        current_time += process.burst_time
        
        # Calculate completion and derived times
        process.completion_time = current_time
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
    
    statistics = calculate_statistics(processes_sorted)
    return execution_timeline, statistics

def shortest_job_first(processes):
    """
    Shortest Job First (SJF) Scheduling Algorithm
    
    Non-preemptive algorithm that selects the process with shortest burst time.
    Optimal for minimizing average waiting time but can cause starvation.
    
    Args:
        processes: List of Process objects
    
    Returns:
        Tuple containing (execution_timeline, statistics)
    """
    if not processes:
        return [], {}
    
    processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    ready_queue = []
    completed = []
    current_time = 0
    execution_timeline = []
    
    while len(completed) < len(processes_copy):
        # Add newly arrived processes to ready queue
        for process in processes_copy:
            if process.arrival_time <= current_time and process not in ready_queue and process not in completed:
                ready_queue.append(process)
        
        if ready_queue:
            # Select process with shortest burst time (SJF)
            selected_process = min(ready_queue, key=lambda p: (p.burst_time, p.pid))
            ready_queue.remove(selected_process)
            
            # Set timing information
            selected_process.start_time = current_time
            selected_process.response_time = current_time - selected_process.arrival_time
            
            # Execute the process
            execution_timeline.append({
                'pid': selected_process.pid,
                'start': current_time,
                'end': current_time + selected_process.burst_time,
                'duration': selected_process.burst_time
            })
            
            current_time += selected_process.burst_time
            
            # Complete the process
            selected_process.completion_time = current_time
            selected_process.turnaround_time = selected_process.completion_time - selected_process.arrival_time
            selected_process.waiting_time = selected_process.turnaround_time - selected_process.burst_time
            completed.append(selected_process)
        else:
            # No process ready, advance time to next arrival
            next_arrival = min([p.arrival_time for p in processes_copy if p not in completed])
            current_time = next_arrival
    
    statistics = calculate_statistics(completed)
    return execution_timeline, statistics

def round_robin(processes, quantum=3):
    """
    Round Robin (RR) Scheduling Algorithm
    
    Preemptive algorithm where each process gets a fixed time slice (quantum).
    Fair allocation but overhead from context switching.
    
    Args:
        processes: List of Process objects
        quantum: Time slice for each process (default: 3)
    
    Returns:
        Tuple containing (execution_timeline, statistics)
    """
    if not processes:
        return [], {}
    
    processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    ready_queue = []
    completed = []
    current_time = 0
    execution_timeline = []
    
    # Add initially ready processes
    for process in processes_copy:
        if process.arrival_time == 0:
            ready_queue.append(process)
    
    while len(completed) < len(processes_copy):
        # Add newly arrived processes to ready queue
        for process in processes_copy:
            if (process.arrival_time <= current_time and 
                process not in ready_queue and 
                process not in completed and 
                process.remaining_time > 0):
                ready_queue.append(process)
        
        if ready_queue:
            current_process = ready_queue.pop(0)  # Get first process in queue
            
            # Set response time on first execution
            if current_process.response_time == -1:
                current_process.response_time = current_time - current_process.arrival_time
                current_process.start_time = current_time
            
            # Determine execution time (quantum or remaining time)
            execution_time = min(quantum, current_process.remaining_time)
            
            # Execute for the determined time
            execution_timeline.append({
                'pid': current_process.pid,
                'start': current_time,
                'end': current_time + execution_time,
                'duration': execution_time
            })
            
            current_time += execution_time
            current_process.remaining_time -= execution_time
            
            # Check if process is complete
            if current_process.remaining_time == 0:
                current_process.completion_time = current_time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed.append(current_process)
            else:
                # Process not complete, add back to ready queue
                ready_queue.append(current_process)
        else:
            # No process ready, advance time to next arrival
            next_arrivals = [p.arrival_time for p in processes_copy 
                           if p.arrival_time > current_time and p not in completed]
            if next_arrivals:
                current_time = min(next_arrivals)
    
    statistics = calculate_statistics(completed)
    return execution_timeline, statistics

def priority_scheduling(processes):
    """
    Priority Scheduling Algorithm
    
    Non-preemptive algorithm where processes are selected based on priority.
    Lower priority number = higher priority. Can cause starvation.
    
    Args:
        processes: List of Process objects
    
    Returns:
        Tuple containing (execution_timeline, statistics)
    """
    if not processes:
        return [], {}
    
    processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    ready_queue = []
    completed = []
    current_time = 0
    execution_timeline = []
    
    while len(completed) < len(processes_copy):
        # Add newly arrived processes to ready queue
        for process in processes_copy:
            if process.arrival_time <= current_time and process not in ready_queue and process not in completed:
                ready_queue.append(process)
        
        if ready_queue:
            # Select process with highest priority (lowest priority number)
            selected_process = min(ready_queue, key=lambda p: (p.priority, p.pid))
            ready_queue.remove(selected_process)
            
            # Set timing information
            selected_process.start_time = current_time
            selected_process.response_time = current_time - selected_process.arrival_time
            
            # Execute the process
            execution_timeline.append({
                'pid': selected_process.pid,
                'start': current_time,
                'end': current_time + selected_process.burst_time,
                'duration': selected_process.burst_time
            })
            
            current_time += selected_process.burst_time
            
            # Complete the process
            selected_process.completion_time = current_time
            selected_process.turnaround_time = selected_process.completion_time - selected_process.arrival_time
            selected_process.waiting_time = selected_process.turnaround_time - selected_process.burst_time
            completed.append(selected_process)
        else:
            # No process ready, advance time to next arrival
            next_arrival = min([p.arrival_time for p in processes_copy if p not in completed])
            current_time = next_arrival
    
    statistics = calculate_statistics(completed)
    return execution_timeline, statistics

def calculate_statistics(processes):
    """
    Calculate scheduling statistics for the completed processes.
    
    Args:
        processes: List of completed Process objects
    
    Returns:
        Dictionary containing average statistics
    """
    if not processes:
        return {
            'avg_turnaround_time': 0,
            'avg_waiting_time': 0,
            'avg_response_time': 0,
            'total_time': 0,
            'throughput': 0
        }
    
    total_turnaround = sum(p.turnaround_time for p in processes)
    total_waiting = sum(p.waiting_time for p in processes)
    total_response = sum(p.response_time for p in processes)
    total_time = max(p.completion_time for p in processes) if processes else 0
    
    return {
        'avg_turnaround_time': round(total_turnaround / len(processes), 2),
        'avg_waiting_time': round(total_waiting / len(processes), 2),
        'avg_response_time': round(total_response / len(processes), 2),
        'total_time': total_time,
        'throughput': round(len(processes) / total_time, 2) if total_time > 0 else 0
    }