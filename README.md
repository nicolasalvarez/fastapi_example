#  Create virtual environment and install requirements:
* python3 -m venv env
* source env/bin/activate
* pip install -r requirements.txt

# Running the server
* uvicorn main:app --reload

# Interactive API docs
* http://127.0.0.1:8000/docs (Swagger UI)
* http://127.0.0.1:8000/redoc (ReDoc)

# OpenAPI schema
* http://127.0.0.1:8000/openapi.json