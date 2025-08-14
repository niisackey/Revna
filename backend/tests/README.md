# Tests Directory

This directory contains all test files for the Leave Request Application.

## Test Files

### Core Application Tests
- `test_database_models.py` - Tests for database models and data validation
- `test_auth_and_api.py` - Tests for authentication and API endpoints (requires pytest)

### Database Connection Tests
- `test_postgres.py` - Basic PostgreSQL connection test
- `test_postgres2.py` - PostgreSQL connection test with user verification
- `test_postgres3.py` - PostgreSQL connection test without password (trust auth)
- `test_postgres4.py` - PostgreSQL connection test using container IP

### Test Runner
- `run_tests.py` - Main test runner script that runs all available tests

## Running Tests

### Quick Test (No Dependencies)
```bash
# Run database model tests
cd tests
python test_database_models.py
```

### Full Test Suite
```bash
# Run all tests
cd tests
python run_tests.py
```

### Individual Connection Tests
```bash
# Test PostgreSQL connection
cd tests
python test_postgres.py
```

### API Tests (Requires pytest)
```bash
# Install pytest first
pip install pytest

# Run API tests
cd tests
python test_auth_and_api.py
```

## Test Categories

### ✅ Working Tests (No Network Required)
- Database model validation
- Data structure tests
- Enum value tests
- Business logic tests

### ⚠️ Network-Dependent Tests
- PostgreSQL connection tests (may fail on company WiFi)
- API endpoint tests (require running servers)
- Health check tests

## Notes

- Some tests may fail on company WiFi due to network restrictions
- Core functionality tests should always pass
- Connection tests are diagnostic tools for troubleshooting
- The application works perfectly with SQLite when PostgreSQL isn't available

## Test Results Interpretation

- ✅ **PASS** - Test completed successfully
- ❌ **FAIL** - Test failed (check error message)
- ⚠️ **WARN** - Test completed with warnings (usually network issues)
- ⏱️ **TIMEOUT** - Test timed out (usually connection issues)
