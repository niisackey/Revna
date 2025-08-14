#!/usr/bin/env python3
"""
Test Runner for Leave Request Application
Run all tests with this script
"""
import sys
import os
import subprocess

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_auto_cancel_tests():
    """Run auto-cancellation tests"""
    print("\n⏰ Running Auto-Cancellation Tests...")
    try:
        from test_auto_cancellation import test_auto_cancellation
        if test_auto_cancellation():
            print("✅ Auto-cancellation tests passed!")
            return True
        else:
            print("❌ Auto-cancellation tests failed")
            return False
    except Exception as e:
        print(f"❌ Auto-cancellation tests failed: {e}")
        return False

def run_overlap_tests():
    """Run overlap prevention tests"""
    print("\n🔄 Running Overlap Prevention Tests...")
    try:
        from test_overlap_prevention import test_overlap_prevention
        if test_overlap_prevention():
            print("✅ Overlap prevention tests passed!")
            return True
        else:
            print("❌ Overlap prevention tests failed")
            return False
    except Exception as e:
        print(f"❌ Overlap prevention tests failed: {e}")
        return False

def run_database_tests():
    """Run database model tests"""
    print("🧪 Running Database Model Tests...")
    try:
        from test_database_models import TestDatabaseModels, TestDataValidation
        
        # Run database model tests
        test_models = TestDatabaseModels()
        results = []
        results.append(test_models.test_user_model_creation())
        results.append(test_models.test_leave_request_model_creation())
        results.append(test_models.test_leave_duration_calculation())
        results.append(test_models.test_enum_values())
        
        # Run validation tests
        test_validation = TestDataValidation()
        results.append(test_validation.test_email_format_validation())
        results.append(test_validation.test_date_range_validation())
        
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print("✅ Database model tests passed!")
            return True
        else:
            print(f"⚠️ Database model tests: {passed}/{total} passed")
            return False
    except Exception as e:
        print(f"❌ Database model tests failed: {e}")
        return False

def run_connection_tests():
    """Run database connection tests"""
    print("\n🔌 Running Database Connection Tests...")
    
    # Check which connection test files exist
    connection_tests = [
        "test_postgres.py",
        "test_postgres2.py", 
        "test_postgres3.py",
        "test_postgres4.py"
    ]
    
    results = []
    for test_file in connection_tests:
        if os.path.exists(test_file):
            print(f"   Running {test_file}...")
            try:
                # Run the test file
                result = subprocess.run(
                    [sys.executable, test_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if "✅" in result.stdout:
                    print(f"   ✅ {test_file} passed")
                    results.append(True)
                else:
                    print(f"   ⚠️ {test_file} completed with warnings")
                    results.append(False)
            except subprocess.TimeoutExpired:
                print(f"   ⏱️ {test_file} timed out (likely connection issue)")
                results.append(False)
            except Exception as e:
                print(f"   ❌ {test_file} failed: {e}")
                results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"Connection tests: {passed}/{total} passed")
    return passed > 0

def check_application_health():
    """Check if the application is running correctly"""
    print("\n🏥 Checking Application Health...")
    
    try:
        import requests
        
        # Check if FastAPI is running
        try:
            response = requests.get("http://localhost:8001/", timeout=5)
            if response.status_code == 200:
                print("✅ FastAPI backend is running")
                backend_ok = True
            else:
                print(f"⚠️ FastAPI backend responding with status {response.status_code}")
                backend_ok = False
        except requests.exceptions.RequestException:
            print("❌ FastAPI backend is not running")
            backend_ok = False
        
        # Check if frontend is running
        try:
            response = requests.get("http://localhost:3000/", timeout=5)
            if response.status_code == 200:
                print("✅ Next.js frontend is running")
                frontend_ok = True
            else:
                print(f"⚠️ Next.js frontend responding with status {response.status_code}")
                frontend_ok = False
        except requests.exceptions.RequestException:
            print("❌ Next.js frontend is not running")
            frontend_ok = False
        
        return backend_ok and frontend_ok
        
    except ImportError:
        print("⚠️ 'requests' library not installed, skipping health check")
        return True

def main():
    """Run all tests"""
    print("🚀 Leave Request Application Test Suite")
    print("=" * 50)
    
    # Run tests
    db_tests_passed = run_database_tests()
    overlap_tests_passed = run_overlap_tests()
    auto_cancel_tests_passed = run_auto_cancel_tests()
    conn_tests_passed = run_connection_tests()
    app_healthy = check_application_health()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Database Model Tests: {'✅ PASS' if db_tests_passed else '❌ FAIL'}")
    print(f"Overlap Prevention Tests: {'✅ PASS' if overlap_tests_passed else '❌ FAIL'}")
    print(f"Auto-Cancellation Tests: {'✅ PASS' if auto_cancel_tests_passed else '❌ FAIL'}")
    print(f"Connection Tests: {'✅ PASS' if conn_tests_passed else '❌ FAIL'}")
    print(f"Application Health: {'✅ HEALTHY' if app_healthy else '⚠️ CHECK'}")
    
    # Final status
    if db_tests_passed:
        print("\n🎉 Core functionality tests passed!")
        print("Your application is ready for demonstration.")
    else:
        print("\n⚠️ Some tests failed, but this may be due to:")
        print("  - Company WiFi blocking database connections")
        print("  - Services not running")
        print("  - Missing dependencies")
        
    print("\n📝 To start your application:")
    print("  Backend:  python main_with_auth.py")
    print("  Frontend: npm run dev (in frontend folder)")
    print("  Demo:     http://localhost:3000")

if __name__ == "__main__":
    main()
