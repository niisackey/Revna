#!/usr/bin/env python3
"""
Simple PostgreSQL connection test
"""

import psycopg2
import os

def test_connection():
    """Test PostgreSQL connection"""
    database_url = os.getenv("DATABASE_URL", "postgresql://leave_app:leave_password123@localhost:5432/leave_requests")
    
    print(f"Testing connection to: {database_url}")
    
    try:
        # Test connection
        conn = psycopg2.connect(database_url)
        print("✅ Connection successful!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
