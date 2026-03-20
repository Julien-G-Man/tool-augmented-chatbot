from sqlalchemy import text

def list_departments(db):
    query = text("""
        SELECT
            D.Dnumber,
            D.Dname,
            D.Mgr_ssn,
            E.Fname AS manager_fname,
            E.Lname AS manager_lname
        FROM Department D
        LEFT JOIN Employee E ON E.Ssn = D.Mgr_ssn
        ORDER BY D.Dnumber
    """)
    rows = db.execute(query).mappings().all()
    return [
        {
            "department_number": row["Dnumber"],
            "department_name": row["Dname"],
            "manager_ssn": row["Mgr_ssn"],
            "manager_start_date": None,
            "manager_name": (
                f"{row['manager_fname']} {row['manager_lname']}"
                if row["manager_fname"] and row["manager_lname"]
                else None
            ),
        }
        for row in rows
    ]


def list_projects(db):
    query = text("""
        SELECT
            P.Pnumber,
            P.Pname,
            P.Plocation,
            P.Dnum,
            D.Dname
        FROM Project P
        LEFT JOIN Department D ON D.Dnumber = P.Dnum
        ORDER BY P.Pnumber
    """)
    rows = db.execute(query).mappings().all()
    return [
        {
            "project_number": row["Pnumber"],
            "project_name": row["Pname"],
            "project_location": row["Plocation"],
            "department_number": row["Dnum"],
            "department_name": row["Dname"],
        }
        for row in rows
    ]


def list_employees(db):
    query = text("""
        SELECT
            E.Ssn,
            E.Fname,
            E.Minit,
            E.Lname,
            E.Bdate,
            E.Address,
            E.Sex,
            E.Salary,
            E.Super_ssn,
            E.Dno,
            D.Dname
        FROM Employee E
        LEFT JOIN Department D ON D.Dnumber = E.Dno
        ORDER BY E.Lname, E.Fname
    """)
    rows = db.execute(query).mappings().all()
    return [
        {
            "ssn": row["Ssn"],
            "first_name": row["Fname"],
            "middle_initial": row["Minit"],
            "last_name": row["Lname"],
            "birth_date": str(row["Bdate"]) if row["Bdate"] else None,
            "address": row["Address"],
            "sex": row["Sex"],
            "salary": float(row["Salary"]) if row["Salary"] is not None else None,
            "supervisor_ssn": row["Super_ssn"],
            "department_number": row["Dno"],
            "department_name": row["Dname"],
        }
        for row in rows
    ]


def get_employees_by_project(db, project_name: str):
    query = text("""
        SELECT E.Ssn, E.Fname, E.Lname, W.Hours
        FROM Employee E
        JOIN Works_on W ON E.Ssn = W.Essn
        JOIN Project P ON W.Pno = P.Pnumber
        WHERE P.Pname = :project_name
        ORDER BY E.Lname, E.Fname
    """)
    rows = db.execute(query, {"project_name": project_name}).mappings().all()
    return [
        {
            "ssn": row["Ssn"],
            "employee_name": f"{row['Fname']} {row['Lname']}",
            "hours": float(row["Hours"]) if row["Hours"] is not None else None,
        }
        for row in rows
    ]


def get_project_lead(db, project_name: str):
    query = text("""
        SELECT E.Ssn, E.Fname, E.Lname, D.Dname
        FROM Employee E
        JOIN Department D ON E.Ssn = D.Mgr_ssn
        JOIN Project P ON D.Dnumber = P.Dnum
        WHERE P.Pname = :project_name
    """)
    row = db.execute(query, {"project_name": project_name}).mappings().fetchone()
    if row:
        return {
            "project_name": project_name,
            "department_name": row["Dname"],
            "lead_ssn": row["Ssn"],
            "lead_name": f"{row['Fname']} {row['Lname']}",
        }
    return "No lead found"


def get_dependents_by_employee(db, employee_ssn: str):
    query = text("""
        SELECT Dependent_name, Sex, Bdate, Relationship
        FROM Dependent
        WHERE Essn = :employee_ssn
        ORDER BY Dependent_name
    """)
    rows = db.execute(query, {"employee_ssn": employee_ssn}).mappings().all()
    return [
        {
            "dependent_name": row["Dependent_name"],
            "sex": row["Sex"],
            "birth_date": str(row["Bdate"]) if row["Bdate"] else None,
            "relationship": row["Relationship"],
        }
        for row in rows
    ]