"""
Disk Scheduling Simulator
Flask Web Application for Demonstrating Operating System Disk Scheduling

This application simulates different disk scheduling algorithms and provides
an interactive web interface for educational purposes.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime
from disk_scheduler import (
    DiskRequest,
    fcfs_disk_scheduling,
    sstf_disk_scheduling,
    scan_disk_scheduling,
    c_scan_disk_scheduling,
    look_disk_scheduling,
    c_look_disk_scheduling
)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')

# Database configuration
DATABASE = 'disk_scheduler.db'

def get_db_connection():
    """
    Create a connection to the SQLite database.
    Returns a connection object with row factory enabled for easier data access.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def init_database():
    """
    Initialize the database with the disk_requests table.
    This function creates the table structure needed for storing disk request information.
    """
    conn = get_db_connection()
    
    # Create disk_requests table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS disk_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER UNIQUE NOT NULL,
            track_number INTEGER NOT NULL,
            arrival_time INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database when the app starts
with app.app_context():
    init_database()

@app.route('/')
def index():
    """
    Main page route - displays the disk scheduling simulator interface.
    """
    return render_template('index.html')

@app.route('/disk_requests')
def get_disk_requests():
    """
    API endpoint to retrieve all disk requests from the database.
    Returns JSON data of all disk requests for frontend consumption.
    """
    conn = get_db_connection()
    disk_requests = conn.execute(
        'SELECT * FROM disk_requests ORDER BY arrival_time, request_id'
    ).fetchall()
    conn.close()
    
    # Convert sqlite3.Row objects to dictionaries for JSON serialization
    request_list = []
    for disk_request in disk_requests:
        request_list.append({
            'id': disk_request['id'],
            'request_id': disk_request['request_id'],
            'track_number': disk_request['track_number'],
            'arrival_time': disk_request['arrival_time']
        })
    
    return jsonify(request_list)

@app.route('/add_disk_request', methods=['POST'])
def add_disk_request():
    """
    API endpoint to add a new disk request to the system.
    Accepts JSON data with disk request information and stores it in the database.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['request_id', 'track_number']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate input ranges
        if data['track_number'] < 0:
            return jsonify({'error': 'Track number must be non-negative'}), 400
        if data['track_number'] > 199:  # Assuming 200-track disk (0-199)
            return jsonify({'error': 'Track number must be less than 200'}), 400
        
        arrival_time = data.get('arrival_time', 0)
        if arrival_time < 0:
            return jsonify({'error': 'Arrival time must be non-negative'}), 400
        
        conn = get_db_connection()
        
        # Check if request ID already exists
        existing = conn.execute('SELECT request_id FROM disk_requests WHERE request_id = ?', (data['request_id'],)).fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Request ID already exists'}), 400
        
        # Insert new disk request
        conn.execute('''
            INSERT INTO disk_requests (request_id, track_number, arrival_time)
            VALUES (?, ?, ?)
        ''', (data['request_id'], data['track_number'], arrival_time))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Disk request added successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_disk_request/<int:id>', methods=['PUT'])
def update_disk_request(id):
    """
    API endpoint to update an existing disk request in the system.
    Allows modification of track number and arrival time.
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        
        # Check if request exists
        existing = conn.execute('SELECT * FROM disk_requests WHERE id = ?', (id,)).fetchone()
        if not existing:
            conn.close()
            return jsonify({'error': 'Disk request not found'}), 404
        
        # Validate and update fields
        track_number = data.get('track_number', existing['track_number'])
        arrival_time = data.get('arrival_time', existing['arrival_time'])
        
        # Validate input ranges
        if track_number < 0:
            conn.close()
            return jsonify({'error': 'Track number must be non-negative'}), 400
        if track_number > 199:
            conn.close()
            return jsonify({'error': 'Track number must be less than 200'}), 400
        if arrival_time < 0:
            conn.close()
            return jsonify({'error': 'Arrival time must be non-negative'}), 400
        
        # Update the disk request
        conn.execute('''
            UPDATE disk_requests 
            SET track_number = ?, arrival_time = ?
            WHERE id = ?
        ''', (track_number, arrival_time, id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Disk request updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_disk_request/<int:id>', methods=['DELETE'])
def delete_disk_request(id):
    """
    API endpoint to delete a disk request from the system.
    Removes the request with the specified ID from the database.
    """
    try:
        conn = get_db_connection()
        
        # Check if request exists
        disk_request = conn.execute('SELECT id FROM disk_requests WHERE id = ?', (id,)).fetchone()
        if not disk_request:
            conn.close()
            return jsonify({'error': 'Disk request not found'}), 404
        
        # Delete the request
        conn.execute('DELETE FROM disk_requests WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Disk request deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_disk_requests', methods=['POST'])
def clear_disk_requests():
    """
    API endpoint to clear all disk requests from the system.
    Removes all requests from the database for a fresh start.
    """
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM disk_requests')
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'All disk requests cleared successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/simulate', methods=['POST'])
def simulate_disk_scheduling():
    """
    API endpoint to run disk scheduling simulation.
    Accepts algorithm type and returns head movement sequence and statistics.
    """
    try:
        print("!!!!!!!!!! RUNNING THE NEWEST CODE !!!!!!!!!") 
        data = request.get_json()
        algorithm = data.get('algorithm', 'fcfs')
        initial_head_position = data.get('initial_head_position', 50)
        disk_size = data.get('disk_size', 200)
        direction = data.get('direction', 'up')
        
        # Validate algorithm type
        valid_algorithms = ['fcfs', 'sstf', 'scan', 'c_scan', 'look', 'c_look']
        if algorithm not in valid_algorithms:
            return jsonify({'error': f'Invalid algorithm. Must be one of: {valid_algorithms}'}), 400
        
        # Validate initial head position
        if not isinstance(initial_head_position, int) or initial_head_position < 0 or initial_head_position >= disk_size:
            return jsonify({'error': f'Initial head position must be between 0 and {disk_size-1}'}), 400
        
        # Validate direction for SCAN and LOOK
        if algorithm in ['scan', 'look'] and direction not in ['up', 'down']:
            return jsonify({'error': 'Direction must be "up" or "down" for SCAN and LOOK algorithms'}), 400
        
        # Get all disk requests from database
        conn = get_db_connection()
        db_requests = conn.execute(
            'SELECT * FROM disk_requests ORDER BY arrival_time, request_id'
        ).fetchall()
        conn.close()
        
        if not db_requests:
            return jsonify({'error': 'No disk requests found'}), 400
        
        # Convert database requests to DiskRequest objects
        disk_requests = []
        for db_request in db_requests:
            request = DiskRequest(
                request_id=db_request['request_id'],
                track_number=db_request['track_number'],
                arrival_time=db_request['arrival_time']
            )
            disk_requests.append(request)
        
        # Run the selected disk scheduling algorithm
        if algorithm == 'fcfs':
            head_movement, total_seek_time, statistics = fcfs_disk_scheduling(disk_requests, initial_head_position)
        elif algorithm == 'sstf':
            head_movement, total_seek_time, statistics = sstf_disk_scheduling(disk_requests, initial_head_position)
        elif algorithm == 'scan':
            head_movement, total_seek_time, statistics = scan_disk_scheduling(disk_requests, initial_head_position, disk_size, direction)
        elif algorithm == 'c_scan':
            head_movement, total_seek_time, statistics = c_scan_disk_scheduling(disk_requests, initial_head_position, disk_size)
        elif algorithm == 'look':
            head_movement, total_seek_time, statistics = look_disk_scheduling(disk_requests, initial_head_position, direction)
        elif algorithm == 'c_look':
            head_movement, total_seek_time, statistics = c_look_disk_scheduling(disk_requests, initial_head_position)
        else:
            return jsonify({'error': 'Unknown algorithm'}), 400
        
        return jsonify({
            'algorithm': algorithm,
            'head_movement': head_movement,
            'total_seek_time': total_seek_time,
            'statistics': statistics,
            'initial_head_position': initial_head_position,
            'message': f'{algorithm.upper()} simulation completed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Configure Flask to run in debug mode
if __name__ == '__main__':
    # Run the Flask development server
    # host='0.0.0.0' allows external connections (required for Replit)
    # port=5000 is the standard Flask development port
    app.run(host='0.0.0.0', port=5000, debug=True)