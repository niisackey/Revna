# FastAPI Backend for Leave Request Application
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid

app = FastAPI(title="Leave Request API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class LeaveType(str, Enum):
    ANNUAL = "Annual"
    SICK = "Sick"
    UNPAID = "Unpaid"

class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    CANCELLED = "CANCELLED"

# Pydantic Models
class LeaveRequest(BaseModel):
    employee_id: str
    leave_type: LeaveType
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
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str]
    status: LeaveStatus
    created_at: datetime
    updated_at: datetime

class ApprovalDecision(BaseModel):
    decision: str  # "APPROVE" or "DENY"

# In-memory storage (in production, use a proper database)
leave_requests_db = {}

# Mock authentication (simple employee_id check)
def get_current_employee(employee_id: str = "EMP001"):
    return employee_id

@app.get("/")
async def root():
    return {"message": "Leave Request API is running"}

@app.post("/api/leave-requests", response_model=LeaveRequestResponse)
async def create_leave_request(
    request: LeaveRequest,
    current_employee: str = Depends(get_current_employee)
):
    """Create a new leave request"""
    
    # Check for overlapping approved leaves for the same employee
    for existing_request in leave_requests_db.values():
        if (existing_request["employee_id"] == request.employee_id and 
            existing_request["status"] == LeaveStatus.APPROVED):
            existing_start = existing_request["start_date"]
            existing_end = existing_request["end_date"]
            
            # Check for overlap
            if not (request.end_date < existing_start or request.start_date > existing_end):
                raise HTTPException(
                    status_code=400, 
                    detail="Overlapping with existing approved leave"
                )
    
    # Create new leave request
    request_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_request = {
        "id": request_id,
        "employee_id": request.employee_id,
        "leave_type": request.leave_type,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "reason": request.reason,
        "status": LeaveStatus.PENDING,
        "created_at": now,
        "updated_at": now
    }
    
    leave_requests_db[request_id] = new_request
    
    return LeaveRequestResponse(**new_request)

@app.get("/api/leave-requests", response_model=List[LeaveRequestResponse])
async def get_leave_requests(
    employee_id: Optional[str] = None,
    current_employee: str = Depends(get_current_employee)
):
    """Get all leave requests, optionally filtered by employee_id"""
    
    requests = list(leave_requests_db.values())
    
    if employee_id:
        requests = [req for req in requests if req["employee_id"] == employee_id]
    
    return [LeaveRequestResponse(**req) for req in requests]

@app.get("/api/leave-requests/{request_id}", response_model=LeaveRequestResponse)
async def get_leave_request(request_id: str):
    """Get a specific leave request by ID"""
    
    if request_id not in leave_requests_db:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    return LeaveRequestResponse(**leave_requests_db[request_id])

@app.patch("/api/leave-requests/{request_id}/cancel")
async def cancel_leave_request(
    request_id: str,
    current_employee: str = Depends(get_current_employee)
):
    """Cancel a leave request (only if still PENDING)"""
    
    if request_id not in leave_requests_db:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    request_data = leave_requests_db[request_id]
    
    if request_data["status"] != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=400, 
            detail="Can only cancel pending requests"
        )
    
    request_data["status"] = LeaveStatus.CANCELLED
    request_data["updated_at"] = datetime.now()
    
    return {"id": request_id, "status": LeaveStatus.CANCELLED}

@app.patch("/api/leave-requests/{request_id}/decision")
async def approve_or_deny_request(
    request_id: str,
    decision: ApprovalDecision,
    current_employee: str = Depends(get_current_employee)  # In real app, check admin role
):
    """Admin endpoint to approve or deny a leave request"""
    
    if request_id not in leave_requests_db:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    request_data = leave_requests_db[request_id]
    
    if request_data["status"] != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=400, 
            detail="Can only approve/deny pending requests"
        )
    
    if decision.decision == "APPROVE":
        request_data["status"] = LeaveStatus.APPROVED
    elif decision.decision == "DENY":
        request_data["status"] = LeaveStatus.DENIED
    else:
        raise HTTPException(
            status_code=400, 
            detail="Decision must be 'APPROVE' or 'DENY'"
        )
    
    request_data["updated_at"] = datetime.now()
    
    return {"id": request_id, "status": request_data["status"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
