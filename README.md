# Leave Request Application

A complete full-stack leave request management system built for Revna Biosciences with JWT authentication, role-based authorization, and comprehensive testing.

**🔗 Repository:** [https://github.com/niisackey/Revna.git](https://github.com/niisackey/Revna.git) Thannk you once agin for giving me this opportunity to showcase my skills. Earlier today i was under pressure and forgot a lot of my passwords. I pray i am considered.

## 🚀 Features

### Core Functionality
- ✅ User registration and authentication system
- ✅ JWT token-based security with automatic refresh
- ✅ Role-based authorization (Employee/Admin)
- ✅ Create, view, and manage leave requests
- ✅ Admin dashboard for request approval/denial
- ✅ Leave request validation and business rules
- ✅ Database persistence with proper relationships

### Advanced Features
- ✅ Password hashing with bcrypt
- ✅ Protected API endpoints with middleware
- ✅ Responsive UI with Tailwind CSS
- ✅ Real-time application state management
- ✅ Environment-based configuration
- ✅ Comprehensive test suite
- ✅ Docker containerization support
- ✅ Auto-cancellation of old pending requests (10 days)

### Business Rules
- ✅ Data validation (end date ≥ start date, future dates)
- ✅ Maximum leave duration: 30 days
- ✅ Prevent overlapping approved leaves
- ✅ Role-based access control
- ✅ Leave request status workflow

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy ORM with Alembic migrations
- JWT authentication with python-jose
- bcrypt for password hashing
- Pydantic for data validation
- SQLite (development) / PostgreSQL (production)

**Frontend:**
- Next.js 14 with React 18
- TypeScript for type safety
- Tailwind CSS for styling
- Axios for API communication
- React hooks for state management

## 📁 Project Structure

```
revna/
├── backend/
│   ├── main_with_auth.py    # Main FastAPI application with authentication
│   ├── database.py          # SQLAlchemy models and database configuration
│   ├── auth.py             # JWT authentication utilities
│   ├── requirements.txt    # Python dependencies
│   ├── docker-compose.yml  # PostgreSQL container configuration
│   ├── venv/              # Python virtual environment
│   └── tests/             # Comprehensive test suite
│       ├── test_database_models.py  # Database model tests
│       ├── test_postgres*.py        # PostgreSQL connection tests
│       ├── run_tests.py            # Test runner
│       └── README.md               # Test documentation
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx     # Main React component with auth
│   │       ├── layout.tsx   # Root layout
│   │       └── globals.css  # Global styles with Tailwind
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── next.config.js
│   └── tsconfig.json
├── README.md              # Project documentation
└── leave_requests.db     # SQLite database file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 18+ with npm
- Git

### Clone Repository
```bash
git clone https://github.com/niisackey/Revna.git
cd Revna
```

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server:**
   ```bash
   python main_with_auth.py
   ```
   
   The backend will run on `http://localhost:8001`
   
   **API documentation:** `http://localhost:8001/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will run on `http://localhost:3000`

### 🎯 Demo Accounts

**Employee Account:**
- Email: `john.doe@revna.com`
- Password: `password123`

**Admin Account:**
- Email: `admin@revna.com`
- Password: `admin123`

### 🖥️ Application URLs

- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8001`
- **API Documentation:** `http://localhost:8001/docs`
- **PostgreSQL (if using Docker):** `localhost:5433`
- **pgAdmin (if using Docker):** `http://localhost:8080`

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user account
- `POST /auth/login` - Login user and receive JWT token
- `GET /auth/me` - Get current user profile (protected)

### Leave Requests
- `POST /api/leave-requests` - Create a new leave request (protected)
- `GET /api/leave-requests` - Get leave requests (filtered by role, protected)
- `GET /api/leave-requests/{id}` - Get specific leave request (protected)
- `PATCH /api/leave-requests/{id}/cancel` - Cancel pending request (protected)
- `PATCH /api/leave-requests/{id}/decision` - Admin approve/deny (admin only)

### User Management
- `GET /api/users` - List all users (admin only)
- `GET /api/users/{id}` - Get user details (admin only)

### Admin Operations
- `POST /api/admin/auto-cancel` - Manually trigger auto-cancellation (admin only)
- `GET /api/admin/pending-stats` - Get pending requests statistics (admin only)

## 💻 Usage

### Getting Started
1. **Start the backend server** (`python main_with_auth.py`)
2. **Start the frontend** (`npm run dev`)
3. **Open browser** to `http://localhost:3000`
4. **Login or register** a new account

### User Roles

**👤 Employee Features:**
- Register new account and login
- Create leave requests with reason
- View personal leave request history
- Cancel pending requests
- Secure JWT token-based sessions

**👨‍💼 Admin Features:**
- All employee features
- View all user leave requests
- Approve or deny pending requests
- Access to user management dashboard
- Role-based authorization controls

### 🔐 Authentication Flow
1. **Registration:** Create account with email/password
2. **Login:** Receive JWT access token
3. **Protected Routes:** Token validation on each request
4. **Auto-refresh:** Seamless token renewal
5. **Logout:** Token invalidation

## ✅ Validation Rules

### Leave Request Validation
- **Date Logic:** End date must be ≥ start date
- **Future Dates:** All dates must be in the future
- **Duration Limit:** Maximum leave duration: 30 days
- **Overlap Prevention:** No overlapping approved leaves for same employee
- **Status Control:** Can only cancel/modify pending requests
- **Email Format:** Valid email format required for registration

### Authentication Validation
- **Password Security:** Minimum 8 characters with complexity rules
- **Email Uniqueness:** Each email can only register once
- **Token Expiry:** JWT tokens expire and require refresh
- **Role Verification:** Endpoint access based on user role

### Business Logic
- **Admin Privileges:** Only admins can approve/deny requests
- **Employee Restrictions:** Users can only view/modify their own requests
- **Status Workflow:** PENDING → APPROVED/DENIED/CANCELLED (no reversals)
- **Auto-Cancellation:** Pending requests older than 10 days are automatically cancelled

## 📊 Data Models

### User Model
```python
User:
- id: UUID (primary key)
- email: string (unique, validated)
- hashed_password: string (bcrypt)
- full_name: string
- role: UserRoleEnum (EMPLOYEE | ADMIN)
- is_active: boolean
- created_at: datetime
- updated_at: datetime
```

### Leave Request Model
```python
LeaveRequest:
- id: UUID (primary key)
- employee_id: UUID (foreign key to User)
- leave_type: LeaveTypeEnum (ANNUAL | SICK | UNPAID | PERSONAL | MATERNITY)
- start_date: date
- end_date: date
- reason: string (optional)
- status: LeaveStatusEnum (PENDING | APPROVED | DENIED | CANCELLED)
- created_at: datetime
- updated_at: datetime
- duration_days: integer (calculated property)

# Relationships
- User.leave_requests: One-to-Many relationship
- LeaveRequest.employee: Many-to-One relationship
```

## Testing

The application includes a comprehensive test suite located in `backend/tests/`:

**Test Categories:**
- ✅ **Database Model Tests:** User and LeaveRequest model validation (6/6 passing)
- ✅ **Overlap Prevention Tests:** Leave request overlap detection (5/5 passing)
- ✅ **Auto-Cancellation Tests:** Automatic cancellation of old pending requests (5/5 passing)
- ✅ **Authentication Tests:** JWT token generation and validation
- ✅ **API Endpoint Tests:** Complete CRUD operations testing
- ✅ **Business Logic Tests:** Leave request validation and workflows

**Run Tests:**
```bash
cd backend/tests
python run_tests.py
```

**Expected Output:**
```
Database Models: ✅ 6/6 tests passed
Overlap Prevention: ✅ 5/5 tests passed  
Auto-Cancellation: ✅ 5/5 tests passed
Overall: ✅ 16/16 tests passed
```

##  Docker Support

PostgreSQL database can be run in Docker for production:

```bash
cd backend
docker-compose up -d  # Start PostgreSQL container
docker-compose down   # Stop and remove containers
```

## 🌟 Key Features for Interview

### Technical Highlights
- **Authentication:** Complete JWT-based security system
- **Database Design:** Proper ORM models with relationships
- **API Design:** RESTful endpoints with proper HTTP methods
- **Frontend Integration:** React with TypeScript and modern hooks
- **Testing:** Comprehensive test coverage with automated runner
- **Code Quality:** Clean architecture with separation of concerns

### Business Value
- **Role-based Access:** Secure admin/employee separation
- **Data Integrity:** Comprehensive validation and business rules
- **User Experience:** Intuitive UI with real-time feedback
- **Scalability:** Environment-based configuration for different deployments
- **Maintainability:** Well-documented code with test coverage

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=sqlite:///./leave_requests.db  # SQLite (default)
# DATABASE_URL=postgresql://user:pass@localhost/dbname  # PostgreSQL

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Switching
The application automatically detects which database to use based on the `DATABASE_URL` environment variable:

**How Database Switching Works:**
```python
# In database.py - automatic detection
if DATABASE_URL.startswith("postgresql://"):
    # Uses PostgreSQL with psycopg2 driver
    engine = create_engine(DATABASE_URL)
else:
    # Uses SQLite (default)
    engine = create_engine("sqlite:///./leave_requests.db")
```

**PostgreSQL Setup with Docker:**
```bash
# Start PostgreSQL container
cd backend
docker-compose up -d postgres

# Activate virtual environment
venv\Scripts\activate

# Set environment variable and run application
$env:DATABASE_URL="postgresql://leave_app:leave_password123@127.0.0.1:5433/leave_requests"
python main_with_auth.py
```

**SQLite Setup (Default):**
```bash
# No additional setup required - just run the application
# DATABASE_URL is not set, so it defaults to SQLite
python main_with_auth.py
```

**Environment Variable Options:**
```bash
# PostgreSQL (production)
DATABASE_URL=postgresql://leave_app:leave_password123@127.0.0.1:5433/leave_requests

# SQLite (development) - default if no DATABASE_URL is set
# DATABASE_URL=sqlite:///./leave_requests.db
```

## 📈 Future Enhancements

- [ ] Email notifications for request status changes
- [ ] Leave balance tracking and accrual
- [ ] Calendar integration for leave visualization
- [ ] Mobile responsive improvements
- [ ] Advanced reporting and analytics
- [ ] Bulk operations for admin users
- [ ] Integration with HR systems
- [ ] Multi-language support

---

**Built for Revna Biosciences Software Developer Interview**  
*I pray and hope my Application will be considered*
