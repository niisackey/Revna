# Database configuration
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import enum
from datetime import datetime
import os

# Database URL - Use environment variable or default to SQLite for company WiFi compatibility
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leave_requests.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class LeaveTypeEnum(enum.Enum):
    ANNUAL = "Annual"
    SICK = "Sick"
    UNPAID = "Unpaid"

class LeaveStatusEnum(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    CANCELLED = "CANCELLED"

class UserRoleEnum(enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    ADMIN = "ADMIN"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.EMPLOYEE)
    department = Column(String(100))
    is_active = Column(String(10), default="true")  # Boolean compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    employee_id = Column(String(50), nullable=False, index=True)
    leave_type = Column(Enum(LeaveTypeEnum), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)
    status = Column(Enum(LeaveStatusEnum), default=LeaveStatusEnum.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Initialize with sample data
def init_sample_data():
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    db = SessionLocal()
    try:
        # Check if users already exist
        if db.query(User).count() == 0:
            # Create sample users with hashed passwords
            users = [
                User(
                    employee_id="EMP001",
                    name="John Doe",
                    email="john.doe@revna.com",
                    hashed_password=pwd_context.hash("password123"),
                    role=UserRoleEnum.EMPLOYEE,
                    department="Engineering"
                ),
                User(
                    employee_id="EMP002",
                    name="Jane Smith",
                    email="jane.smith@revna.com",
                    hashed_password=pwd_context.hash("password123"),
                    role=UserRoleEnum.EMPLOYEE,
                    department="Marketing"
                ),
                User(
                    employee_id="ADMIN001",
                    name="Admin User",
                    email="admin@revna.com",
                    hashed_password=pwd_context.hash("admin123"),
                    role=UserRoleEnum.ADMIN,
                    department="HR"
                )
            ]
            
            for user in users:
                db.add(user)
            
            db.commit()
            print("Sample users created successfully!")
            print("Default credentials:")
            print("- john.doe@revna.com / password123 (Employee)")
            print("- jane.smith@revna.com / password123 (Employee)")
            print("- admin@revna.com / admin123 (Admin)")
    
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()
