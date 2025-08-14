# PostgreSQL Setup Guide for Leave Request Application

This guide will help you set up PostgreSQL for the Leave Request application as required by the assignment.

## Option 1: Using Docker (Recommended - Easiest)

### Prerequisites
- Docker and Docker Compose installed
- Available port 5432 for PostgreSQL

### Steps
1. **Start PostgreSQL with Docker Compose:**
   ```bash
   cd C:\Users\niisa\revna\backend
   docker-compose up -d postgres
   ```

2. **Verify the database is running:**
   ```bash
   docker ps
   ```
   You should see the `leave_requests_db` container running.

3. **The database is now ready!**
   - Database: `leave_requests`
   - User: `leave_app`
   - Password: `leave_password123`
   - Port: `5432`

## Option 2: Local PostgreSQL Installation

### Prerequisites
1. **Download and install PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Download PostgreSQL 15 or later
   - Install with default settings
   - Remember the password you set for the `postgres` user

### Steps
1. **Open PostgreSQL command line (psql) or pgAdmin**

2. **Create the database and user:**
   ```sql
   CREATE DATABASE leave_requests;
   CREATE USER leave_app WITH PASSWORD 'leave_password123';
   GRANT ALL PRIVILEGES ON DATABASE leave_requests TO leave_app;
   ```

3. **Update connection if using different credentials:**
   Edit `database.py` and update the DATABASE_URL if needed.

## Verification

Once PostgreSQL is running, you can verify the setup:

1. **Start the FastAPI server:**
   ```bash
   cd C:\Users\niisa\revna\backend
   .\venv\Scripts\Activate.ps1
   python main_with_auth.py
   ```

2. **Check the logs:**
   You should see:
   ```
   Sample users created successfully!
   Default credentials:
   - john.doe@revna.com / password123 (Employee)
   - jane.smith@revna.com / password123 (Employee)
   - admin@revna.com / admin123 (Admin)
   INFO: Uvicorn running on http://0.0.0.0:8001
   ```

3. **Test the application:**
   - Open: http://localhost:3000
   - Login with demo credentials
   - Create and manage leave requests

## Database Connection Details

- **Host:** localhost
- **Port:** 5432
- **Database:** leave_requests
- **Username:** leave_app
- **Password:** leave_password123
- **Connection URL:** `postgresql://leave_app:leave_password123@localhost:5432/leave_requests`

## Troubleshooting

### Common Issues:

1. **Port 5432 already in use:**
   - Stop existing PostgreSQL service
   - Or change port in docker-compose.yml

2. **Connection refused:**
   - Ensure PostgreSQL is running
   - Check firewall settings
   - Verify connection details

3. **Permission denied:**
   - Ensure user has correct privileges
   - Check password is correct

---

✅ **The application now uses PostgreSQL as required by the assignment!**
