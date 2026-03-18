from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.api import db_queries

router = APIRouter()


@router.get("/departments")
def departments(db: Session = Depends(get_db)):
    return db_queries.list_departments(db)


@router.get("/projects")
def projects(db: Session = Depends(get_db)):
    return db_queries.list_projects(db)


@router.get("/employees")
def employees(db: Session = Depends(get_db)):
    return db_queries.list_employees(db)


@router.get("/employees/by-project")
def employees_by_project(project_name: str, db: Session = Depends(get_db)):
    return db_queries.get_employees_by_project(db, project_name)

@router.get("/project/lead")
def project_lead(project_name: str, db: Session = Depends(get_db)):
    return db_queries.get_project_lead(db, project_name)


@router.get("/dependents/by-employee")
def dependents_by_employee(employee_ssn: str, db: Session = Depends(get_db)):
    return db_queries.get_dependents_by_employee(db, employee_ssn)


@router.get("/db/health")
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"db_status": "connected"}
    except Exception as exc:
        return {"db_status": "error", "details": str(exc)}