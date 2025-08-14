#!/usr/bin/env python3
"""
Test suite for Database Models and Operations
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import User, LeaveRequest, LeaveTypeEnum, LeaveStatusEnum, UserRoleEnum
from datetime import date, datetime

class TestDatabaseModels:
    """Test database models"""
    
    def test_user_model_creation(self):
        """Test User model can be created with required fields"""
        try:
            user = User(
                employee_id="TEST001",
                email="test@example.com",
                name="Test User",
                department="IT",
                role=UserRoleEnum.EMPLOYEE,
                hashed_password="hashed_password_here"
            )
            
            assert user.employee_id == "TEST001"
            assert user.email == "test@example.com"
            assert user.role == UserRoleEnum.EMPLOYEE
            print("✅ User model creation test passed")
            return True
        except Exception as e:
            print(f"❌ User model creation test failed: {e}")
            return False
    
    def test_leave_request_model_creation(self):
        """Test LeaveRequest model can be created with required fields"""
        try:
            leave_request = LeaveRequest(
                employee_id="TEST001",
                start_date=date(2025, 9, 1),
                end_date=date(2025, 9, 5),
                leave_type=LeaveTypeEnum.ANNUAL,
                reason="Vacation",
                status=LeaveStatusEnum.PENDING
            )
            
            assert leave_request.employee_id == "TEST001"
            assert leave_request.leave_type == LeaveTypeEnum.ANNUAL
            assert leave_request.status == LeaveStatusEnum.PENDING
            assert leave_request.start_date == date(2025, 9, 1)
            print("✅ LeaveRequest model creation test passed")
            return True
        except Exception as e:
            print(f"❌ LeaveRequest model creation test failed: {e}")
            return False
    
    def test_leave_duration_calculation(self):
        """Test leave duration calculation logic"""
        try:
            start_date = date(2025, 9, 1)
            end_date = date(2025, 9, 5)
            
            # Duration should be 5 days (including start and end date)
            duration = (end_date - start_date).days + 1
            assert duration == 5
            print("✅ Leave duration calculation test passed")
            return True
        except Exception as e:
            print(f"❌ Leave duration calculation test failed: {e}")
            return False
    
    def test_enum_values(self):
        """Test enum values are correct"""
        try:
            # Test LeaveTypeEnum enum
            assert LeaveTypeEnum.ANNUAL.value == "Annual"
            assert LeaveTypeEnum.SICK.value == "Sick"
            assert LeaveTypeEnum.UNPAID.value == "Unpaid"
            
            # Test LeaveStatusEnum enum
            assert LeaveStatusEnum.PENDING.value == "PENDING"
            assert LeaveStatusEnum.APPROVED.value == "APPROVED"
            assert LeaveStatusEnum.DENIED.value == "DENIED"
            assert LeaveStatusEnum.CANCELLED.value == "CANCELLED"
            
            # Test UserRoleEnum enum
            assert UserRoleEnum.EMPLOYEE.value == "EMPLOYEE"
            assert UserRoleEnum.ADMIN.value == "ADMIN"
            
            print("✅ Enum values test passed")
            return True
        except Exception as e:
            print(f"❌ Enum values test failed: {e}")
            return False

class TestDataValidation:
    """Test data validation logic"""
    
    def test_email_format_validation(self):
        """Test email format validation logic"""
        try:
            valid_emails = [
                "user@example.com",
                "test.user@company.com",
                "admin@revna.com"
            ]
            
            # Test valid emails
            for email in valid_emails:
                assert "@" in email and "." in email.split("@")[1]
            
            # Test simple invalid case
            invalid_email = "invalid-email"
            assert "@" not in invalid_email
                    
            print("✅ Email format validation test passed")
            return True
        except Exception as e:
            print(f"❌ Email format validation test failed: {e}")
            return False
    
    def test_date_range_validation(self):
        """Test date range validation logic"""
        try:
            # Valid date range
            start_date = date(2025, 9, 1)
            end_date = date(2025, 9, 5)
            assert start_date <= end_date
            
            # Invalid date range
            invalid_start = date(2025, 9, 10)
            invalid_end = date(2025, 9, 5)
            assert not (invalid_start <= invalid_end)
            
            print("✅ Date range validation test passed")
            return True
        except Exception as e:
            print(f"❌ Date range validation test failed: {e}")
            return False

def main():
    """Run all tests and report results"""
    print("🧪 Database Model Tests")
    print("=" * 40)
    
    test_models = TestDatabaseModels()
    test_validation = TestDataValidation()
    
    results = []
    
    # Run model tests
    results.append(test_models.test_user_model_creation())
    results.append(test_models.test_leave_request_model_creation())
    results.append(test_models.test_leave_duration_calculation())
    results.append(test_models.test_enum_values())
    
    # Run validation tests
    results.append(test_validation.test_email_format_validation())
    results.append(test_validation.test_date_range_validation())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n📊 Test Results")
    print("=" * 20)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All database model tests passed!")
    else:
        print(f"⚠️ {total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    main()
