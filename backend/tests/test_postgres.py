#!/usr/bin/env python3
"""
Test PostgreSQL connection directly
"""
import psycopg2
from sqlalchemy import create_engine, text

# Test connection parameters
DB_HOST = "127.0.0.1"
DB_PORT = "5433"
DB_NAME = "leave_requests"
DB_USER = "leave_app"
DB_PASSWORD = "leave_password123"

print("Testing PostgreSQL connection...")

# Test 1: Direct psycopg2 connection
try:
    print("\n1. Testing direct psycopg2 connection...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Direct connection successful!")
    print(f"PostgreSQL version: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Direct connection failed: {e}")

# Test 2: SQLAlchemy connection
try:
    print("\n2. Testing SQLAlchemy connection...")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"Connection string: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_user, current_database()"))
        row = result.fetchone()
        print(f"✅ SQLAlchemy connection successful!")
        print(f"Current user: {row[0]}, Current database: {row[1]}")
except Exception as e:
    print(f"❌ SQLAlchemy connection failed: {e}")

print("\nConnection test completed.")
