# Disk Scheduling Simulator

## Project Overview
This is a Flask-based web application that demonstrates disk scheduling algorithms for operating systems education. The project simulates different disk scheduling algorithms and provides an interactive interface with head movement visualization.

## Recent Changes
- Completely rebuilt as Disk Scheduling Simulator (September 20, 2025)
- Implemented six core disk scheduling algorithms: FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK
- Created interactive web interface with Bootstrap styling
- Added disk head movement visualization using Chart.js
- Implemented SQLite database for disk request storage
- Added comprehensive CRUD operations for disk requests
- Included detailed code comments for educational purposes

## User Preferences
- Student prefers simple, beginner-friendly implementation
- Wants step-by-step comments explaining disk scheduling concepts
- Needs easy local deployment capability
- Requires basic CRUD functionality demonstration

## Project Architecture

### Backend (Flask)
- **app.py**: Main Flask application with all routes and database initialization
- **disk_scheduler.py**: Core disk scheduling algorithms implementation with detailed comments
- **disk_scheduler.db**: SQLite database for disk request storage (auto-created)

### Frontend
- **templates/index.html**: Single-page application with Bootstrap styling for disk scheduling
- **static/css/styles.css**: Custom CSS for enhanced UI with disk-specific styling
- **static/js/disk_app.js**: Frontend JavaScript handling disk request interactions and head movement visualization

### Features Implemented
1. **Disk Request Management**: Create, read, update, delete disk requests (CRUD)
2. **Disk Scheduling Algorithms**: 
   - First Come First Serve (FCFS)
   - Shortest Seek Time First (SSTF)
   - SCAN (Elevator Algorithm)
   - C-SCAN (Circular SCAN)
   - LOOK
   - C-LOOK (Circular LOOK)
3. **Head Movement Visualization**: Interactive chart showing disk head movement patterns over time
4. **Performance Statistics**: Calculate and display total seek time, average seek time, throughput
5. **Database**: SQLite for persistent disk request storage
6. **Responsive Design**: Bootstrap-based responsive UI with algorithm descriptions

### Dependencies
- Flask: Web framework
- SQLite3: Database (built into Python)
- Bootstrap 5: Frontend styling
- Chart.js: Data visualization for head movement

## How to Run Locally
1. Make sure Python 3.x is installed
2. Install Flask: `pip install flask`
3. Run the application: `python app.py`
4. Open browser to: `http://localhost:5000`
5. Add disk requests using the form, select an algorithm and initial head position, then run simulation

## Educational Value
This project demonstrates key operating system disk scheduling concepts:
- Disk head movement optimization and seek time minimization
- Trade-offs between different scheduling algorithms (fairness vs efficiency)
- Starvation prevention in disk scheduling
- Performance metrics for disk I/O operations
- Real-world applications of scheduling algorithms in storage systems

The code includes extensive comments explaining each algorithm's logic and disk scheduling decisions, making it ideal for understanding how operating systems optimize disk performance.