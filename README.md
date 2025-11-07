# Contacts Management Web App--Backend
## Overview
This is the backend service for the Contacts Management web application.  
It is built using **Django** and provides a RESTful API to manage contacts information (name, email, phone).  
All contact data is stored in a **SQLite3** database.  
The backend communicates with the frontend hosted at `http://127.0.0.1:5500/Contacts_front_end/index.html` via HTTP requests.

---

## Features
- Add a new contact (name, email, phone)
- View all contacts
- Edit existing contact information
- Delete a contact
- CORS support for frontend connection

---

## Tech Stack
- **Language:** Python 3.x  
- **Framework:** Django 4.x  
- **Database:** SQLite3  
- **CORS:** django-cors-headers  
- **Port:** 8000  


## Project Structure
```
Contacts/           # Django project settings folder
├── init.py
├── asgi.py
├── settings.py
├── urls.py
├── wsgi.py
contacts_app/           # Main application folder
├── migrations
  ├── 0001_initial.py
  ├── __init__.py
├── __init__.py
├── admin.py
├── apps.py
├── models.py           # Contact model
├── tests.py
├── urls.py             # URL routing for contact endpoints
├── views.py            # Views / API logic
README.md               # This documentation
manage.py               # Django project manager
.gitignore              # Files and directories to exclude from 
requirements.txt        # required packages
LICENSE                 # License file (MIT License)
codestyle.md            # Code style and formatting 
```

## Setup Instructions

### 1. Clone and Enter Project
```bash
git clone https://github.com/<your-username>/832301327_contacts_backend.git
cd 832301327_contacts_backend
```
### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```
### 3. Install Dependencies
you need to install:
```bash
pip install -r requirement.txt
```
### 4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
### 5. Run the Server
```bash
python manage.py runserver
```
The server will start at: http://127.0.0.1:8000/

⸻

API Endpoints

Method	Endpoint	Description
GET	/contacts/	Get all contacts
POST	/contacts/	Add a new contact
PUT	/contacts/<id>/	Edit a contact
DELETE	/contacts/<id>/	Delete a contact

Example JSON (POST)

{
  "name": "Wu Jianyuan",
  "email": "wjy@game.ie",
  "phone": "911"
}


⸻

CORS Configuration

This project uses django-cors-headers to allow requests from the frontend.

In settings.py:
```
INSTALLED_APPS = [
    ...
    'corsheaders',
    'contacts_app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500"
]
```

⸻

License

This project is licensed under the MIT License – see the LICENSE file for details.

---
