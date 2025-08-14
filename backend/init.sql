-- PostgreSQL initialization script for Leave Request Application
-- This script will be executed when the PostgreSQL container starts

-- Create the application user
CREATE USER leave_app WITH PASSWORD 'leave_password123';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE leave_requests TO leave_app;
GRANT ALL ON SCHEMA public TO leave_app;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO leave_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO leave_app;
