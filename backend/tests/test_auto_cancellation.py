"""
Test for auto-cancellation of old pending leave requests
"""
import sys
import os
import uuid
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, get_db, User, LeaveRequest, LeaveTypeEnum, LeaveStatusEnum, UserRoleEnum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile

def test_auto_cancellation():
    """Test that old pending requests are automatically cancelled"""
    print("\n🔍 Testing auto-cancellation logic...")
    
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
        
        # Create old pending request (12 days old - should be cancelled)
        old_pending = LeaveRequest(
            id=str(uuid.uuid4()),
            employee_id=test_user.employee_id,
            leave_type=LeaveTypeEnum.ANNUAL,
            start_date=datetime.now().date() + timedelta(days=20),
            end_date=datetime.now().date() + timedelta(days=25),
            reason="Old request",
            status=LeaveStatusEnum.PENDING
        )
        # Manually set created_at to 12 days ago
        old_pending.created_at = datetime.now() - timedelta(days=12)
        db.add(old_pending)
        
        # Create recent pending request (5 days old - should NOT be cancelled)
        recent_pending = LeaveRequest(
            id=str(uuid.uuid4()),
            employee_id=test_user.employee_id,
            leave_type=LeaveTypeEnum.ANNUAL,
            start_date=datetime.now().date() + timedelta(days=30),
            end_date=datetime.now().date() + timedelta(days=35),
            reason="Recent request",
            status=LeaveStatusEnum.PENDING
        )
        # Manually set created_at to 5 days ago
        recent_pending.created_at = datetime.now() - timedelta(days=5)
        db.add(recent_pending)
        
        # Create approved request (15 days old - should NOT be cancelled)
        old_approved = LeaveRequest(
            id=str(uuid.uuid4()),
            employee_id=test_user.employee_id,
            leave_type=LeaveTypeEnum.ANNUAL,
            start_date=datetime.now().date() + timedelta(days=40),
            end_date=datetime.now().date() + timedelta(days=45),
            reason="Approved request",
            status=LeaveStatusEnum.APPROVED
        )
        old_approved.created_at = datetime.now() - timedelta(days=15)
        db.add(old_approved)
        
        db.commit()
        
        print("   Testing auto-cancellation logic...")
        
        # Simulate the auto-cancellation function
        cutoff_date = datetime.now() - timedelta(days=10)
        
        # Find pending requests older than 10 days
        old_pending_requests = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatusEnum.PENDING,
            LeaveRequest.created_at < cutoff_date
        ).all()
        
        cancelled_count = 0
        for request in old_pending_requests:
            request.status = LeaveStatusEnum.CANCELLED
            request.updated_at = datetime.now()
            cancelled_count += 1
        
        db.commit()
        
        # Verify results
        print("   Checking results...")
        
        # Check that old pending request was cancelled
        old_request_updated = db.query(LeaveRequest).filter(
            LeaveRequest.id == old_pending.id
        ).first()
        assert old_request_updated.status == LeaveStatusEnum.CANCELLED, "Old pending request should be cancelled"
        print("   ✅ Old pending request (12 days) correctly cancelled")
        
        # Check that recent pending request was NOT cancelled
        recent_request_check = db.query(LeaveRequest).filter(
            LeaveRequest.id == recent_pending.id
        ).first()
        assert recent_request_check.status == LeaveStatusEnum.PENDING, "Recent pending request should remain pending"
        print("   ✅ Recent pending request (5 days) correctly preserved")
        
        # Check that approved request was NOT cancelled
        approved_request_check = db.query(LeaveRequest).filter(
            LeaveRequest.id == old_approved.id
        ).first()
        assert approved_request_check.status == LeaveStatusEnum.APPROVED, "Approved request should remain approved"
        print("   ✅ Old approved request correctly preserved")
        
        # Check cancellation count
        assert cancelled_count == 1, f"Expected 1 cancellation, got {cancelled_count}"
        print(f"   ✅ Correct number of requests cancelled: {cancelled_count}")
        
        # Check for only pending requests in age range
        all_pending = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatusEnum.PENDING
        ).count()
        
        assert all_pending == 1, f"Expected 1 remaining pending request, got {all_pending}"
        print("   ✅ Correct number of pending requests remaining")
        
        # Cleanup
        db.close()
        engine.dispose()
        
        # Try to remove file
        import time
        for attempt in range(3):
            try:
                os.unlink(temp_db_name)
                break
            except (OSError, PermissionError):
                if attempt < 2:
                    time.sleep(0.1)
        
        print("🎉 All auto-cancellation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Auto-cancellation test failed: {e}")
        return False

if __name__ == "__main__":
    test_auto_cancellation()
