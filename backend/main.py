from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from backend.finance_tracker.tracker import FinanceTracker
from fastapi.middleware.cors import  CORSMiddleware
from datetime import date
from backend.database import initialize_database

app = FastAPI()
tracker = FinanceTracker()

@app.on_event("startup")
def on_startup():
    initialize_database()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

#Pydantic models
class ExpenseRequest(BaseModel):
    category: str
    amount: float

class IncomeRequest(BaseModel):
    source: str
    amount: float

class LoginRequest(BaseModel):
    identifier: str
    password: str

class UserRegistration(BaseModel):
    email: str
    password: str
    name: str
    DOB: date
    username: Optional[str] = None


# API Endpoints
@app.post("/register")
def register(user: UserRegistration):
    result = tracker.register(user.email, user.password, user.name, user.DOB, user.username)
    if "✅" in result:
        return {"message": result}
    raise HTTPException(400, detail=result)


@app.post("/login")
def login(credentials: LoginRequest):
    result = tracker.login(credentials.identifier, credentials.password)
    if "✅" in result:
        return {"message": result}
    raise HTTPException(401, detail=result)


@app.post("/expense")
def add_expense(value: ExpenseRequest):
    result = tracker.add_expense(value.category, value.amount)
    if "✅" in result:
        return {"message": result}
    raise HTTPException(401, detail=result)


@app.post("/income")
def add_income(value: IncomeRequest):
    result = tracker.add_income(value.amount, value.source)
    if "✅" in result:
        return {"message": result}
    raise HTTPException(401, detail=result)

@app.get("/report")
def get_report():
    report = tracker.view_report()
    if report:
        return report