# Database Query Tools
database_tools = [
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

# RAG Tools - for searching company documents
rag_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_company_documents",
            "description": "Search company PDF documents and policies for relevant information. Use this when questions are about company documents, policies, procedures, or any information that might be in PDFs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or question to find relevant documents"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_indexed_documents",
            "description": "List all documents that have been indexed in the RAG system",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Combine all tools
tools = database_tools + rag_tools