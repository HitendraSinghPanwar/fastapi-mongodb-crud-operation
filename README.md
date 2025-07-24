# fastapi-mongodb-crud-operation
FastAPI-based asynchronous API that performs full CRUD operations using MongoDB with Motor (async driver).


# Installation & Setup

# 1. Clone the repository

- git clone https://github.com/your-username/fastapi-mongodb-crud-operation.git
- cd fastapi-mongodb-crud-operation

# 2. Create and activate a virtual environment

- python -m venv venv
- venv\Scripts\activate

# 3. Install dependencies

pip install -r requirements.txt

# 4. Setup .env file
Create a .env file in the root folder:(Replace your_database_name with your actual DB name.)

- MONGO_URL=mongodb://localhost:27017
- MONGO_DB=your_database_name

# Run the Server
- uvicorn main:app --reload
- Go to: http://127.0.0.1:8000

# Testing

- You can use curl, Postman, or Swagger UI for testing the APIs.
- Swagger UI available at:
- http://127.0.0.1:8000/docs

