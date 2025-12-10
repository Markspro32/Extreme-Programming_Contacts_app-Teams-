# Contact Manager - Backend

This is the backend part of a contact management application, built with Python and Flask, using SQLite as the database.

## Features

- RESTful API for contact operations
- SQLite database for data storage
- CORS support

## Setup and Run

1. Clone this repository
2. Install dependencies:
pip install flask flask-cors
3. Run the application:
cd srcpython 
app.py
4. The server will start at http://localhost:5000

## API Endpoints

- GET /contacts - Get all contacts
- GET /contacts/{id} - Get a specific contact
- POST /contacts - Add a new contact
- PUT /contacts/{id} - Update a contact
- DELETE /contacts/{id} - Delete a contact