#!/bin/bash

# Navigate to the backend directory and install dependencies
cd backend
# pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload
