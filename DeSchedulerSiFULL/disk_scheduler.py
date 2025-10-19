"""
Disk Scheduling Algorithms Implementation
Contains implementations of various disk scheduling algorithms for the simulator.

This module provides the core disk scheduling logic for:
- First Come First Serve (FCFS)
- Shortest Seek Time First (SSTF)
- SCAN (Elevator Algorithm)
- C-SCAN (Circular SCAN)
- LOOK
- C-LOOK (Circular LOOK)
"""

class DiskRequest:
    """
    DiskRequest class to represent a single disk I/O request.
    Contains all necessary information for disk scheduling simulation.
    """
    def __init__(self, request_id, track_number, arrival_time):
        self.request_id = request_id
        self.track_number = track_number
        self.arrival_time = arrival_time
        self.service_time = -1  # When the request gets serviced
        self.response_time = -1  # Time from arrival to service start
        self.completed = False

def fcfs_disk_scheduling(requests, initial_head_position):
    """
    First Come First Serve (FCFS) Disk Scheduling Algorithm
    
    Services disk requests in the order they arrive.
    Simple but may cause excessive head movement.
    
    Args:
        requests: List of DiskRequest objects
        initial_head_position: Starting position of disk head
    
    Returns:
        Tuple containing (head_movement_sequence, total_seek_time, statistics)
    """
    if not requests:
        return [], 0, {}
    
    # Sort requests by arrival time
    sorted_requests = sorted(requests, key=lambda r: (r.arrival_time, r.request_id))
    
    head_position = initial_head_position
    current_time = 0
    total_seek_time = 0
    head_movement_sequence = [{'position': head_position, 'time': current_time, 'request': None}]
    
    for request in sorted_requests:
        # Wait for request arrival if necessary
        if current_time < request.arrival_time:
            current_time = request.arrival_time
        
        # Calculate seek time (distance to move)
        seek_time = abs(head_position - request.track_number)
        total_seek_time += seek_time
        
        # Move head to request position
        head_position = request.track_number
        current_time += seek_time if seek_time > 0 else 1  # Minimum 1 unit for processing
        
        # Record request completion
        request.service_time = current_time
        request.response_time = current_time - request.arrival_time
        request.completed = True
        
        # Record head movement
        head_movement_sequence.append({
            'position': head_position,
            'time': current_time,
            'request': request.request_id,
            'seek_distance': seek_time
        })
    
    statistics = calculate_disk_statistics(sorted_requests, total_seek_time, current_time)
    return head_movement_sequence, total_seek_time, statistics

def sstf_disk_scheduling(requests, initial_head_position):
    """
    Shortest Seek Time First (SSTF) Disk Scheduling Algorithm
    
    Always services the request closest to the current head position.
    Minimizes seek time but can cause starvation.
    
    Args:
        requests: List of DiskRequest objects
        initial_head_position: Starting position of disk head
    
    Returns:
        Tuple containing (head_movement_sequence, total_seek_time, statistics)
    """
    if not requests:
        return [], 0, {}
    
    requests_copy = [DiskRequest(r.request_id, r.track_number, r.arrival_time) for r in requests]
    pending_requests = []
    completed_requests = []
    
    head_position = initial_head_position
    current_time = 0
    total_seek_time = 0
    head_movement_sequence = [{'position': head_position, 'time': current_time, 'request': None}]
    
    while len(completed_requests) < len(requests_copy):
        # Add newly arrived requests to pending queue
        for request in requests_copy:
            if (request.arrival_time <= current_time and 
                request not in pending_requests and 
                request not in completed_requests):
                pending_requests.append(request)
        
        if pending_requests:
            # Select request with shortest seek time from current position
            closest_request = min(pending_requests, 
                                key=lambda r: abs(r.track_number - head_position))
            pending_requests.remove(closest_request)
            
            # Calculate seek time
            seek_time = abs(head_position - closest_request.track_number)
            total_seek_time += seek_time
            
            # Move head to request position
            head_position = closest_request.track_number
            current_time += seek_time if seek_time > 0 else 1
            
            # Complete the request
            closest_request.service_time = current_time
            closest_request.response_time = current_time - closest_request.arrival_time
            closest_request.completed = True
            completed_requests.append(closest_request)
            
            # Record head movement
            head_movement_sequence.append({
                'position': head_position,
                'time': current_time,
                'request': closest_request.request_id,
                'seek_distance': seek_time
            })
        else:
            # No pending requests, advance time to next arrival
            next_arrivals = [r.arrival_time for r in requests_copy if r not in completed_requests]
            if next_arrivals:
                current_time = min(next_arrivals)
    
    statistics = calculate_disk_statistics(completed_requests, total_seek_time, current_time)
    return head_movement_sequence, total_seek_time, statistics

def scan_disk_scheduling(requests, initial_head_position, disk_size=200, direction='up'):
    """
    SCAN (Elevator) Disk Scheduling Algorithm
    
    Head moves in one direction servicing all requests, then reverses direction.
    Good for reducing variance in response time.
    
    Args:
        requests: List of DiskRequest objects
        initial_head_position: Starting position of disk head
        disk_size: Total number of tracks (default: 200)
        direction: Initial direction ('up' or 'down')
    
    Returns:
        Tuple containing (head_movement_sequence, total_seek_time, statistics)
    """
    if not requests:
        return [], 0, {}
    
    requests_copy = [DiskRequest(r.request_id, r.track_number, r.arrival_time) for r in requests]
    for r in requests_copy:
        r.completed = False
    completed_requests = []
    
    head_position = initial_head_position
    current_time = 0
    total_seek_time = 0
    head_movement_sequence = [{'position': head_position, 'time': current_time, 'request': None}]
    going_up = direction == 'up'
    
    while len(completed_requests) < len(requests_copy):
        # Get requests that have arrived at current time
        available_requests = [r for r in requests_copy if r.arrival_time <= current_time and not r.completed]
        
        if not available_requests:
            # No requests available, advance time to next arrival
            next_arrivals = [r.arrival_time for r in requests_copy if not r.completed]
            if next_arrivals:
                current_time = min(next_arrivals)
                continue
            else:
                break
        if going_up:
            # Find requests in current direction (up)
            candidates = [r for r in available_requests if r.track_number >= head_position]
            if candidates:
                # Service closest request in up direction
                next_request = min(candidates, key=lambda r: r.track_number)
            else:
                # No more requests in up direction, reverse and go to highest remaining
                going_up = False
                candidates = [r for r in available_requests if r.track_number < head_position]
                next_request = max(candidates, key=lambda r: r.track_number) if candidates else None
        else:
            # Find requests in current direction (down)
            candidates = [r for r in available_requests if r.track_number <= head_position]
            if candidates:
                # Service closest request in down direction
                next_request = max(candidates, key=lambda r: r.track_number)
            else:
                # No more requests in down direction, reverse and go to lowest remaining
                going_up = True
                candidates = [r for r in available_requests if r.track_number > head_position]
                next_request = min(candidates, key=lambda r: r.track_number) if candidates else None
        
        if next_request:
            # Calculate seek time
            seek_time = abs(head_position - next_request.track_number)
            total_seek_time += seek_time
            
            # Move head to request position
            head_position = next_request.track_number
            current_time += seek_time if seek_time > 0 else 1
            
            # Complete the request
            next_request.service_time = current_time
            next_request.response_time = current_time - next_request.arrival_time
            next_request.completed = True
            available_requests.remove(next_request)
            completed_requests.append(next_request)
            
            # Record head movement
            head_movement_sequence.append({
                'position': head_position,
                'time': current_time,
                'request': next_request.request_id,
                'seek_distance': seek_time
            })
    
    statistics = calculate_disk_statistics(completed_requests, total_seek_time, current_time)
    return head_movement_sequence, total_seek_time, statistics

def c_scan_disk_scheduling(requests, initial_head_position, disk_size=200):
    """
    C-SCAN (Circular SCAN) Disk Scheduling Algorithm
    
    Head moves in one direction, then jumps to the beginning and continues.
    Provides more uniform wait times than SCAN.
    
    Args:
        requests: List of DiskRequest objects
        initial_head_position: Starting position of disk head
        disk_size: Total number of tracks (default: 200)
    
    Returns:
        Tuple containing (head_movement_sequence, total_seek_time, statistics)
    """
    if not requests:
        return [], 0, {}
    
    requests_copy = [DiskRequest(r.request_id, r.track_number, r.arrival_time) for r in requests]
    for r in requests_copy:
        r.completed = False
    completed_requests = []
    
    head_position = initial_head_position
    current_time = 0
    total_seek_time = 0
    head_movement_sequence = [{'position': head_position, 'time': current_time, 'request': None}]
    
    while len(completed_requests) < len(requests_copy):
        # Get requests that have arrived at current time
        available_requests = [r for r in requests_copy if r.arrival_time <= current_time and not r.completed]
        
        if not available_requests:
            # No requests available, advance time to next arrival
            next_arrivals = [r.arrival_time for r in requests_copy if not r.completed]
            if next_arrivals:
                current_time = min(next_arrivals)
                continue
            else:
                break
        # Find requests at or above current position
        candidates = [r for r in available_requests if r.track_number >= head_position]
        
        if candidates:
            # Service next request in ascending order
            next_request = min(candidates, key=lambda r: r.track_number)
        else:
            # No requests ahead, jump to beginning (lowest track)
            next_request = min(available_requests, key=lambda r: r.track_number)
            # Add seek time for jumping to beginning
            jump_seek_time = head_position  # Seek to track 0, then to lowest request
            total_seek_time += jump_seek_time
            current_time += jump_seek_time
            head_position = 0
            
            # Record the jump
            head_movement_sequence.append({
                'position': 0,
                'time': current_time,
                'request': None,
                'seek_distance': jump_seek_time,
                'action': 'jump_to_start'
            })
        
        # Calculate seek time to next request
        seek_time = abs(head_position - next_request.track_number)
        total_seek_time += seek_time
        
        # Move head to request position
        head_position = next_request.track_number
        current_time += seek_time if seek_time > 0 else 1
        
        # Complete the request
        next_request.service_time = current_time
        next_request.response_time = current_time - next_request.arrival_time
        next_request.completed = True
        available_requests.remove(next_request)
        completed_requests.append(next_request)
        
        # Record head movement
        head_movement_sequence.append({
            'position': head_position,
            'time': current_time,
            'request': getattr(next_request, 'request_id', None),
            'seek_distance': seek_time
        })
    
    statistics = calculate_disk_statistics(completed_requests, total_seek_time, current_time)
    return head_movement_sequence, total_seek_time, statistics

def look_disk_scheduling(requests, initial_head_position, direction='up'):
    """
    LOOK Disk Scheduling Algorithm
    
    Similar to SCAN but head only goes as far as the highest/lowest request,
    then reverses direction. No need to go to disk ends.
    
    Args:
        requests: List of DiskRequest objects
        initial_head_position: Starting position of disk head
        direction: Initial direction ('up' or 'down')
    
    Returns:
        Tuple containing (head_movement_sequence, total_seek_time, statistics)
    """
    if not requests:
        return [], 0, {}
    
    requests_copy = [DiskRequest(r.request_id, r.track_number, r.arrival_time) for r in requests]
    completed_requests = []
    
    head_position = initial_head_position
    current_time = 0
    total_seek_time = 0
    head_movement_sequence = [{'position': head_position, 'time': current_time, 'request': None}]
    going_up = direction == 'up'
    
    # Initialize completed flag for all requests
    for r in requests_copy:
        r.completed = False
    
    while len(completed_requests) < len(requests_copy):
        # Get requests that have arrived at current time
        available_requests = [r for r in requests_copy if r.arrival_time <= current_time and not r.completed]
        
        if not available_requests:
            # No requests available, advance time to next arrival
            next_arrivals = [r.arrival_time for r in requests_copy if not r.completed]
            if next_arrivals:
                current_time = min(next_arrivals)
                continue
            else:
                break
        if going_up:
            # Find requests at or above current position
            candidates = [r for r in available_requests if r.track_number >= head_position]
            if candidates:
                # Service next closest request in up direction
                next_request = min(candidates, key=lambda r: r.track_number)
            else:
                # No more requests above, reverse direction to highest remaining below
                going_up = False
                candidates = [r for r in available_requests if r.track_number < head_position]
                next_request = max(candidates, key=lambda r: r.track_number) if candidates else None
        else:
            # Find requests at or below current position
            candidates = [r for r in available_requests if r.track_number <= head_position]
            if candidates:
                # Service next closest request in down direction
                next_request = max(candidates, key=lambda r: r.track_number)
            else:
                # No more requests below, reverse direction to lowest remaining above
                going_up = True
                candidates = [r for r in available_requests if r.track_number > head_position]
                next_request = min(candidates, key=lambda r: r.track_number) if candidates else None
        
        if next_request:
            # Calculate seek time
            seek_time = abs(head_position - next_request.track_number)
            total_seek_time += seek_time
            
            # Move head to request position
            head_position = next_request.track_number
            current_time += seek_time if seek_time > 0 else 1
            
            # Complete the request
            next_request.service_time = current_time
            next_request.response_time = current_time - next_request.arrival_time
            next_request.completed = True
            available_requests.remove(next_request)
            completed_requests.append(next_request)
            
            # Record head movement
            head_movement_sequence.append({
                'position': head_position,
                'time': current_time,
                'request': next_request.request_id,
                'seek_distance': seek_time
            })
    
    statistics = calculate_disk_statistics(completed_requests, total_seek_time, current_time)
    return head_movement_sequence, total_seek_time, statistics

def c_look_disk_scheduling(requests, initial_head_position):
    """
    C-LOOK (Circular LOOK) Disk Scheduling Algorithm
    
    Similar to C-SCAN but head only goes to the highest request,
    then jumps to the lowest request and continues upward.
    
    Args:
        requests: List of DiskRequest objects
        initial_head_position: Starting position of disk head
    
    Returns:
        Tuple containing (head_movement_sequence, total_seek_time, statistics)
    """
    if not requests:
        return [], 0, {}
    
    requests_copy = [DiskRequest(r.request_id, r.track_number, r.arrival_time) for r in requests]
    completed_requests = []
    
    head_position = initial_head_position
    current_time = 0
    total_seek_time = 0
    head_movement_sequence = [{'position': head_position, 'time': current_time, 'request': None}]
    
    # Initialize completed flag for all requests
    for r in requests_copy:
        r.completed = False
    
    while len(completed_requests) < len(requests_copy):
        # Get requests that have arrived at current time
        available_requests = [r for r in requests_copy if r.arrival_time <= current_time and not r.completed]
        
        if not available_requests:
            # No requests available, advance time to next arrival
            next_arrivals = [r.arrival_time for r in requests_copy if not r.completed]
            if next_arrivals:
                current_time = min(next_arrivals)
                continue
            else:
                break

        # Find requests at or above current position
        candidates = [r for r in available_requests if r.track_number >= head_position]
        
        next_request = None
        if candidates:
            # Service next request in ascending order
            next_request = min(candidates, key=lambda r: r.track_number)
        else:
            # No requests ahead, jump to lowest remaining request
            next_request = min(available_requests, key=lambda r: r.track_number)
        
        # Calculate seek time to the determined next request
        seek_time = abs(head_position - next_request.track_number)
        total_seek_time += seek_time
        
        # Move head to request position
        head_position = next_request.track_number
        current_time += seek_time if seek_time > 0 else 1
        
        # Complete the request
        next_request.service_time = current_time
        next_request.response_time = current_time - next_request.arrival_time
        next_request.completed = True
        completed_requests.append(next_request)
        
        # Record the single, correct head movement
        head_movement_sequence.append({
            'position': head_position,
            'time': current_time,
            'request': next_request.request_id,
            'seek_distance': seek_time
        })
    
    statistics = calculate_disk_statistics(completed_requests, total_seek_time, current_time)
    return head_movement_sequence, total_seek_time, statistics

def calculate_disk_statistics(completed_requests, total_seek_time, total_time):
    """
    Calculate disk scheduling statistics for the completed requests.
    
    Args:
        completed_requests: List of completed DiskRequest objects
        total_seek_time: Total seek time across all requests
        total_time: Total time to complete all requests
    
    Returns:
        Dictionary containing disk performance statistics
    """
    if not completed_requests:
        return {
            'total_requests': 0,
            'total_seek_time': 0,
            'avg_seek_time': 0,
            'avg_response_time': 0,
            'total_completion_time': 0,
            'throughput': 0
        }
    
    total_response_time = sum(r.response_time for r in completed_requests)
    
    return {
        'total_requests': len(completed_requests),
        'total_seek_time': total_seek_time,
        'avg_seek_time': round(total_seek_time / len(completed_requests), 2),
        'avg_response_time': round(total_response_time / len(completed_requests), 2),
        'total_completion_time': total_time,
        'throughput': round(len(completed_requests) / total_time, 2) if total_time > 0 else 0
    }