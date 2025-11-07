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
Yuxiang-Xie_832301327_Contacts-Web-APP_back_end/
├── Contacts/                         # Django project configuration folder
│   ├── init.py
│   ├── asgi.py                       # ASGI server config
│   ├── settings.py                   # Global project settings
│   ├── urls.py                       # Root URL routing
│   └── wsgi.py                       # WSGI server config
│
├── contacts_app/                     # Main application handling Contacts CRUD logic
│   ├── init.py
│   ├── admin.py                      # Django admin registration
│   ├── apps.py                       # App config
│   ├── models.py                     # Contact model definitions
│   ├── views.py                      # API view logic (CRUD endpoints)
│   ├── urls.py                       # App-level URL routing
│   ├── serializers.py                # DRF serializers (if used)
│   └── migrations/                   # Database schema migrations
│       └── init.py
│
├── .gitignore                        # Git version control ignore rules
├── LICENSE                           # MIT License
├── README.md                         # Documentation file
├── codestyle.md                      # Backend code styling guidelines
├── manage.py                         # Django project management tool
├── pyvenv.cfg                        # Python virtual environment config (auto-generated)
└── requirements.txt                  # Python dependencies list
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
