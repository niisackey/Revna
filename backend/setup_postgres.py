# PostgreSQL Setup Script
import psycopg2
from psycopg2 import sql
import sys

def create_database():
    """Create PostgreSQL database and user for the leave request application"""
    
    # Database connection parameters
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',  # Default PostgreSQL superuser
        'password': 'password'  # Change this to your PostgreSQL password
    }
    
    # Database and user to create
    database_name = 'leave_requests'
    app_user = 'leave_app'
    app_password = 'leave_password123'
    
    try:
        # Connect to PostgreSQL server (to default database)
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (database_name,)
        )
        
        if cursor.fetchone():
            print(f"Database '{database_name}' already exists.")
        else:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(database_name)
                )
            )
            print(f"Database '{database_name}' created successfully!")
        
        # Check if user exists
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            (app_user,)
        )
        
        if cursor.fetchone():
            print(f"User '{app_user}' already exists.")
        else:
            # Create user
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(app_user)
                ),
                (app_password,)
            )
            print(f"User '{app_user}' created successfully!")
        
        # Grant privileges
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(database_name),
                sql.Identifier(app_user)
            )
        )
        print(f"Privileges granted to '{app_user}' on database '{database_name}'")
        
        cursor.close()
        conn.close()
        
        print("\n✅ PostgreSQL setup completed successfully!")
        print(f"📊 Database: {database_name}")
        print(f"👤 User: {app_user}")
        print(f"🔐 Password: {app_password}")
        print(f"🔗 Connection URL: postgresql://{app_user}:{app_password}@localhost:5432/{database_name}")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL error: {e}")
        print("\n💡 Make sure:")
        print("1. PostgreSQL is installed and running")
        print("2. You can connect with the postgres user")
        print("3. Update the password in this script")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🐘 PostgreSQL Database Setup for Leave Request Application")
    print("=" * 60)
    
    success = create_database()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Update database.py with the connection URL")
        print("2. Restart the FastAPI server")
        print("3. The application will create tables automatically")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Install PostgreSQL: https://www.postgresql.org/download/")
        print("2. Start PostgreSQL service")
        print("3. Update the password in this script")
        print("4. Run: pip install psycopg2-binary")
