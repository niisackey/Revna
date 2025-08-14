# FastAPI Backend with Authentication
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
import uuid
import asyncio
from contextlib import asynccontextmanager

# Import authentication and database components
from auth import (
    authenticate_user, create_access_token, verify_token, 
    get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
)
from database import (
    get_db, create_tables, init_sample_data, 
    User, LeaveRequest as DBLeaveRequest,
    LeaveTypeEnum, LeaveStatusEnum, UserRoleEnum
)

# Auto-cancellation function
def auto_cancel_old_pending_requests():
    """Cancel leave requests that have been pending for more than 10 days"""
    try:
        db = next(get_db())
        
        # Calculate the cutoff date (10 days ago)
        cutoff_date = datetime.now() - timedelta(days=10)
        
        # Find pending requests older than 10 days
        old_pending_requests = db.query(DBLeaveRequest).filter(
            DBLeaveRequest.status == LeaveStatusEnum.PENDING,
            DBLeaveRequest.created_at < cutoff_date
        ).all()
        
        cancelled_count = 0
        for request in old_pending_requests:
            request.status = LeaveStatusEnum.CANCELLED
            request.updated_at = datetime.now()
            cancelled_count += 1
        
        if cancelled_count > 0:
            db.commit()
            print(f"🔄 Auto-cancelled {cancelled_count} old pending leave requests")
        
        db.close()
        return cancelled_count
        
    except Exception as e:
        print(f"❌ Error in auto-cancellation: {e}")
        return 0

# Background task for auto-cancellation
async def periodic_auto_cancel():
    """Run auto-cancellation every hour"""
    while True:
        auto_cancel_old_pending_requests()
        # Wait for 1 hour (3600 seconds)
        await asyncio.sleep(3600)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Leave Request API...")
    create_tables()
    init_sample_data()
    
    # Start the background task
    task = asyncio.create_task(periodic_auto_cancel())
    print("⏰ Auto-cancellation task started (checks every hour)")
    
    yield
    
    # Shutdown
    task.cancel()
    print("🛑 Shutting down Leave Request API...")

app = FastAPI(
    title="Leave Request API with Authentication", 
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic Models for API
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    employee_id: str
    department: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    email: str
    role: str
    department: Optional[str]
    created_at: datetime

class LeaveRequestCreate(BaseModel):
    leave_type: str  # "Annual", "Sick", "Unpaid"
    start_date: date
    end_date: date
    reason: Optional[str] = None
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('End date must be >= start date')
        return v
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_dates(cls, v):
        if v < date.today():
            raise ValueError('Dates must be in the future')
        return v

class LeaveRequestResponse(BaseModel):
    id: str
    employee_id: str
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

class ApprovalDecision(BaseModel):
    decision: str  # "APPROVE" or "DENY"

# Dependency to get current user from token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.get("/")
async def root():
    return {"message": "Leave Request API with Authentication is running"}

@app.post("/api/admin/auto-cancel")
async def manual_auto_cancel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger auto-cancellation of old pending requests (Admin only)"""
    if current_user.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    cancelled_count = auto_cancel_old_pending_requests()
    
    return {
        "message": f"Auto-cancellation completed",
        "cancelled_requests": cancelled_count,
        "triggered_by": current_user.email,
        "timestamp": datetime.now()
    }

@app.get("/api/admin/pending-stats")
async def get_pending_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics about pending requests (Admin only)"""
    if current_user.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Count pending requests by age
    now = datetime.now()
    cutoff_10_days = now - timedelta(days=10)
    cutoff_7_days = now - timedelta(days=7)
    cutoff_3_days = now - timedelta(days=3)
    
    total_pending = db.query(DBLeaveRequest).filter(
        DBLeaveRequest.status == LeaveStatusEnum.PENDING
    ).count()
    
    old_pending = db.query(DBLeaveRequest).filter(
        DBLeaveRequest.status == LeaveStatusEnum.PENDING,
        DBLeaveRequest.created_at < cutoff_10_days
    ).count()
    
    week_old = db.query(DBLeaveRequest).filter(
        DBLeaveRequest.status == LeaveStatusEnum.PENDING,
        DBLeaveRequest.created_at < cutoff_7_days,
        DBLeaveRequest.created_at >= cutoff_10_days
    ).count()
    
    recent = db.query(DBLeaveRequest).filter(
        DBLeaveRequest.status == LeaveStatusEnum.PENDING,
        DBLeaveRequest.created_at >= cutoff_3_days
    ).count()
    
    return {
        "total_pending": total_pending,
        "overdue_for_cancellation": old_pending,  # Will be auto-cancelled
        "week_old": week_old,
        "recent": recent,
        "auto_cancel_threshold": "10 days",
        "next_check": "Within 1 hour"
    }

@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if employee_id already exists
    db_emp = db.query(User).filter(User.employee_id == user.employee_id).first()
    if db_emp:
        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        employee_id=user.employee_id,
        hashed_password=hashed_password,
        department=user.department,
        role=UserRoleEnum.EMPLOYEE  # Default role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        employee_id=db_user.employee_id,
        name=db_user.name,
        email=db_user.email,
        role=db_user.role.value,
        department=db_user.department,
        created_at=db_user.created_at
    )

@app.post("/api/auth/login", response_model=Token)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        employee_id=current_user.employee_id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
        department=current_user.department,
        created_at=current_user.created_at
    )

@app.get("/api/users", response_model=List[UserResponse])
async def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all users (admin only)"""
    if current_user.role != UserRoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(User).all()
    return [
        UserResponse(
            id=user.id,
            employee_id=user.employee_id,
            name=user.name,
            email=user.email,
            role=user.role.value,
            department=user.department,
            created_at=user.created_at
        )
        for user in users
    ]

@app.post("/api/leave-requests", response_model=LeaveRequestResponse)
async def create_leave_request(
    request: LeaveRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new leave request"""
    
    # Check for overlapping approved leaves
    overlapping = db.query(DBLeaveRequest).filter(
        DBLeaveRequest.employee_id == current_user.employee_id,
        DBLeaveRequest.status == LeaveStatusEnum.APPROVED,
        DBLeaveRequest.start_date <= request.end_date,
        DBLeaveRequest.end_date >= request.start_date
    ).first()
    
    if overlapping:
        raise HTTPException(
            status_code=400, 
            detail="Overlapping with existing approved leave"
        )
    
    # Validate leave duration (max 30 days)
    duration = (request.end_date - request.start_date).days + 1
    if duration > 30:
        raise HTTPException(
            status_code=400,
            detail="Leave duration cannot exceed 30 days"
        )
    
    # Create new leave request
    request_id = str(uuid.uuid4())
    
    # Convert string leave_type to enum
    try:
        leave_type_enum = LeaveTypeEnum(request.leave_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid leave type")
    
    db_request = DBLeaveRequest(
        id=request_id,
        employee_id=current_user.employee_id,
        leave_type=leave_type_enum,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason,
        status=LeaveStatusEnum.PENDING
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    return LeaveRequestResponse(
        id=db_request.id,
        employee_id=db_request.employee_id,
        leave_type=db_request.leave_type.value,
        start_date=db_request.start_date,
        end_date=db_request.end_date,
        reason=db_request.reason,
        status=db_request.status.value,
        created_at=db_request.created_at,
        updated_at=db_request.updated_at
    )

@app.get("/api/leave-requests", response_model=List[LeaveRequestResponse])
async def get_leave_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leave requests - employees see only their own, admins see all"""
    
    query = db.query(DBLeaveRequest)
    
    # If not admin, only show user's own requests
    if current_user.role != UserRoleEnum.ADMIN:
        query = query.filter(DBLeaveRequest.employee_id == current_user.employee_id)
    
    requests = query.order_by(DBLeaveRequest.created_at.desc()).all()
    
    return [
        LeaveRequestResponse(
            id=req.id,
            employee_id=req.employee_id,
            leave_type=req.leave_type.value,
            start_date=req.start_date,
            end_date=req.end_date,
            reason=req.reason,
            status=req.status.value,
            created_at=req.created_at,
            updated_at=req.updated_at
        )
        for req in requests
    ]

@app.patch("/api/leave-requests/{request_id}/cancel")
async def cancel_leave_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a leave request (only your own and only if pending)"""
    
    request = db.query(DBLeaveRequest).filter(DBLeaveRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    # Check if user owns this request
    if request.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="You can only cancel your own requests")
    
    if request.status != LeaveStatusEnum.PENDING:
        raise HTTPException(
            status_code=400, 
            detail="Can only cancel pending requests"
        )
    
    request.status = LeaveStatusEnum.CANCELLED
    request.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"id": request_id, "status": LeaveStatusEnum.CANCELLED.value}

@app.patch("/api/leave-requests/{request_id}/decision")
async def approve_or_deny_request(
    request_id: str,
    decision: ApprovalDecision,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to approve or deny a leave request"""
    
    # Check if user is admin
    if current_user.role != UserRoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    request = db.query(DBLeaveRequest).filter(DBLeaveRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    if request.status != LeaveStatusEnum.PENDING:
        raise HTTPException(
            status_code=400, 
            detail="Can only approve/deny pending requests"
        )
    
    if decision.decision == "APPROVE":
        request.status = LeaveStatusEnum.APPROVED
    elif decision.decision == "DENY":
        request.status = LeaveStatusEnum.DENIED
    else:
        raise HTTPException(
            status_code=400, 
            detail="Decision must be 'APPROVE' or 'DENY'"
        )
    
    request.updated_at = datetime.utcnow()
    db.commit()
    
    return {"id": request_id, "status": request.status.value}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
