#!/usr/bin/env python3
"""
Database Configuration Switcher
Easily switch between SQLite and PostgreSQL
"""
import os
import argparse

def update_database_config(db_type):
    """Update the database configuration in database.py"""
    
    database_file = "database.py"
    
    # Read current file
    with open(database_file, 'r') as f:
        content = f.read()
    
    if db_type == "sqlite":
        new_line = 'DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leave_requests.db")'
        print("✅ Switching to SQLite database")
        print("   - Good for: Company WiFi, local development, quick testing")
        print("   - File location: ./leave_requests.db")
        
    elif db_type == "postgres":
        new_line = 'DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://leave_app:leave_password123@127.0.0.1:5432/leave_requests")'
        print("✅ Switching to PostgreSQL database")
        print("   - Good for: Production, interview demonstration")
        print("   - Requires: Docker container running (docker-compose up -d postgres)")
        
    else:
        print("❌ Invalid database type. Use 'sqlite' or 'postgres'")
        return
    
    # Find the DATABASE_URL line and replace it
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('DATABASE_URL = os.getenv'):
            lines[i] = new_line
            break
    
    # Write back to file
    with open(database_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Database configuration updated!")
    print(f"   To use: Restart your FastAPI server")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Switch database configuration')
    parser.add_argument('database', choices=['sqlite', 'postgres'], 
                        help='Database type to switch to')
    
    args = parser.parse_args()
    update_database_config(args.database)
