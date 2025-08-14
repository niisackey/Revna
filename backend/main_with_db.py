# FastAPI Backend for Leave Request Application with PostgreSQL
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy.orm import Session
import uuid

# Import database components
from database import (
    get_db, create_tables, init_sample_data, 
    User, LeaveRequest as DBLeaveRequest,
    LeaveTypeEnum, LeaveStatusEnum, UserRoleEnum
)

app = FastAPI(title="Leave Request API with Database", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models for API
class LeaveRequestCreate(BaseModel):
    employee_id: str
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

class UserResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    email: str
    role: str
    department: Optional[str]
    created_at: datetime

class ApprovalDecision(BaseModel):
    decision: str  # "APPROVE" or "DENY"

# Startup event to create tables and sample data
@app.on_event("startup")
async def startup_event():
    create_tables()
    init_sample_data()

# Helper function to get user by employee_id
def get_user_by_employee_id(db: Session, employee_id: str):
    return db.query(User).filter(User.employee_id == employee_id).first()

# Mock authentication - in real app, use JWT tokens
def get_current_user(employee_id: str = "EMP001", db: Session = Depends(get_db)):
    user = get_user_by_employee_id(db, employee_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/")
async def root():
    return {"message": "Leave Request API with Database is running"}

@app.get("/api/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return users

@app.get("/api/users/{employee_id}", response_model=UserResponse)
async def get_user(employee_id: str, db: Session = Depends(get_db)):
    """Get a specific user by employee ID"""
    user = get_user_by_employee_id(db, employee_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/leave-requests", response_model=LeaveRequestResponse)
async def create_leave_request(
    request: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new leave request"""
    
    # Verify employee exists
    employee = get_user_by_employee_id(db, request.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check for overlapping approved leaves
    overlapping = db.query(DBLeaveRequest).filter(
        DBLeaveRequest.employee_id == request.employee_id,
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
        employee_id=request.employee_id,
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
    employee_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all leave requests, optionally filtered by employee_id"""
    
    query = db.query(DBLeaveRequest)
    
    if employee_id:
        query = query.filter(DBLeaveRequest.employee_id == employee_id)
    
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

@app.get("/api/leave-requests/{request_id}", response_model=LeaveRequestResponse)
async def get_leave_request(request_id: str, db: Session = Depends(get_db)):
    """Get a specific leave request by ID"""
    
    request = db.query(DBLeaveRequest).filter(DBLeaveRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    return LeaveRequestResponse(
        id=request.id,
        employee_id=request.employee_id,
        leave_type=request.leave_type.value,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason,
        status=request.status.value,
        created_at=request.created_at,
        updated_at=request.updated_at
    )

@app.patch("/api/leave-requests/{request_id}/cancel")
async def cancel_leave_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a leave request (only if still PENDING)"""
    
    request = db.query(DBLeaveRequest).filter(DBLeaveRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin endpoint to approve or deny a leave request"""
    
    # Check if user is admin (in real app, use proper role checking)
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
