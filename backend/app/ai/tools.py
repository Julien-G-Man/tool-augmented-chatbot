tools = [
    {
        "type": "function",
        "function": {
            "name": "list_departments",
            "description": "List all departments and their manager info",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "List all projects and the department each project belongs to",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_employees",
            "description": "List employees with core profile and department information",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_employees_by_project",
            "description": "Get employees working on a specific project",
            "parameters": {
                "type": "object",
                "properties": {"project_name": {"type": "string"}},
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_lead",
            "description": "Get the lead of a project",
            "parameters": {
                "type": "object",
                "properties": {"project_name": {"type": "string"}},
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dependents_by_employee",
            "description": "Get all dependents for a specific employee SSN",
            "parameters": {
                "type": "object",
                "properties": {"employee_ssn": {"type": "string"}},
                "required": ["employee_ssn"]
            }
        }
    }
]