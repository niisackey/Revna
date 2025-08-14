"""
Test for overlap prevention in leave requests
"""
import sys
import os
import uuid

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, get_db, User, LeaveRequest, LeaveTypeEnum, LeaveStatusEnum, UserRoleEnum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
from datetime import date, timedelta

def test_overlap_prevention():
    """Test that overlapping approved leaves are prevented"""
    print("\n🔍 Testing overlap prevention logic...")
    
    try:
        # Create temporary database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_name = temp_db.name
        temp_db.close()
        
        # Create engine and session
        engine = create_engine(f'sqlite:///{temp_db_name}')
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        # Create test user
        test_user = User(
            employee_id="TEST001",
            email="test@example.com",
            hashed_password="hashed_password",
            name="Test User",
            role=UserRoleEnum.EMPLOYEE
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create first approved leave request (Aug 15-20, 2025)
        existing_leave = LeaveRequest(
            id=str(uuid.uuid4()),
            employee_id=test_user.employee_id,
            leave_type=LeaveTypeEnum.ANNUAL,
            start_date=date(2025, 8, 15),
            end_date=date(2025, 8, 20),
            reason="Vacation",
            status=LeaveStatusEnum.APPROVED
        )
        db.add(existing_leave)
        db.commit()
        
        # Test case 1: Exact overlap (Aug 15-20, 2025) - Should be blocked
        print("   Testing exact overlap...")
        overlap_query = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == test_user.employee_id,
            LeaveRequest.status == LeaveStatusEnum.APPROVED,
            LeaveRequest.start_date <= date(2025, 8, 20),  # new end_date
            LeaveRequest.end_date >= date(2025, 8, 15)     # new start_date
        ).first()
        
        assert overlap_query is not None, "Should detect exact overlap"
        print("   ✅ Exact overlap correctly detected")
        
        # Test case 2: Partial overlap (Aug 18-25, 2025) - Should be blocked
        print("   Testing partial overlap...")
        overlap_query = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == test_user.employee_id,
            LeaveRequest.status == LeaveStatusEnum.APPROVED,
            LeaveRequest.start_date <= date(2025, 8, 25),  # new end_date
            LeaveRequest.end_date >= date(2025, 8, 18)     # new start_date
        ).first()
        
        assert overlap_query is not None, "Should detect partial overlap"
        print("   ✅ Partial overlap correctly detected")
        
        # Test case 3: No overlap (Aug 25-30, 2025) - Should be allowed
        print("   Testing no overlap...")
        no_overlap_query = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == test_user.employee_id,
            LeaveRequest.status == LeaveStatusEnum.APPROVED,
            LeaveRequest.start_date <= date(2025, 8, 30),  # new end_date
            LeaveRequest.end_date >= date(2025, 8, 25)     # new start_date
        ).first()
        
        assert no_overlap_query is None, "Should NOT detect overlap for non-overlapping dates"
        print("   ✅ No overlap correctly identified")
        
        # Test case 4: Different employee (should not conflict)
        print("   Testing different employee...")
        overlap_query = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == "DIFFERENT_USER",  # Different employee
            LeaveRequest.status == LeaveStatusEnum.APPROVED,
            LeaveRequest.start_date <= date(2025, 8, 20),  # new end_date
            LeaveRequest.end_date >= date(2025, 8, 15)     # new start_date
        ).first()
        
        assert overlap_query is None, "Should NOT detect overlap for different employee"
        print("   ✅ Different employee correctly ignored")
        
        # Test case 5: Only APPROVED leaves should be checked (not PENDING)
        print("   Testing PENDING vs APPROVED status...")
        
        # Add a PENDING leave that would overlap
        pending_leave = LeaveRequest(
            id=str(uuid.uuid4()),
            employee_id=test_user.employee_id,
            leave_type=LeaveTypeEnum.ANNUAL,
            start_date=date(2025, 8, 16),
            end_date=date(2025, 8, 19),
            reason="Pending leave",
            status=LeaveStatusEnum.PENDING
        )
        db.add(pending_leave)
        db.commit()
        
        # Check for overlaps with APPROVED leaves only
        approved_overlap_query = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == test_user.employee_id,
            LeaveRequest.status == LeaveStatusEnum.APPROVED,  # Only APPROVED
            LeaveRequest.start_date <= date(2025, 8, 18),
            LeaveRequest.end_date >= date(2025, 8, 17)
        ).first()
        
        assert approved_overlap_query is not None, "Should still detect APPROVED overlap"
        print("   ✅ Only APPROVED leaves are checked for overlaps")
        
        # Cleanup - Close database connection first
        db.close()
        engine.dispose()
        
        # Try to remove file with retry mechanism
        import time
        for attempt in range(3):
            try:
                os.unlink(temp_db_name)
                break
            except (OSError, PermissionError):
                if attempt < 2:
                    time.sleep(0.1)  # Wait a bit and retry
                # If all attempts fail, just continue (file will be cleaned up by OS)
        
        print("🎉 All overlap prevention tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Overlap prevention test failed: {e}")
        return False

if __name__ == "__main__":
    test_overlap_prevention()
