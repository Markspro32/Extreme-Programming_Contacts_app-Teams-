## Contacts Management Web App

### Overview

This project is a **full-stack contacts manager** built with **Django 5**.  
It serves both:

- A **single-page web UI** (HTML/CSS/JS) rendered by Django
- A **JSON API** for managing contacts

Each contact can have:

- Multiple contact methods (phone, email, social media, address)
- Optional labels for each method (e.g. “Work”, “Home”)
- A **primary** flag per method type
- A **bookmarked** flag to mark “frequently accessed” contacts

The app also supports **Excel import/export** of the address book.

---

## Features

- **Contact CRUD**
  - Create, read, update, delete contacts
  - REST-style JSON endpoints under `/contacts/`
- **Multiple contact methods per contact**
  - Types: `phone`, `email`, `social_media`, `address`
  - Optional label per method
  - Mark methods as **Primary**
- **Bookmarks / Frequently accessed**
  - Toggle bookmark with a star button
  - Bookmarked contacts appear in a **Frequently Accessed** section
- **Excel import & export**
  - Export all contacts and methods to `contacts_export.xlsx`
  - Import contacts from an Excel file in the same format
- **Modern frontend**
  - Single-page UI (`index.html`) with:
    - Dynamic add/edit/delete of contacts
    - Add/remove multiple contact methods
    - Bookmark toggle
    - Import/Export buttons
- **CORS-friendly API**
  - Configured with `django-cors-headers` (if you call the API from another origin)

---

## Tech Stack

- **Language**: Python 3.x
- **Framework**: Django 5.2.7
- **Database**: SQLite (default Django DB)
- **Frontend**: Vanilla JS + HTML + CSS (served by Django)
- **Excel handling**: `pandas` + `openpyxl`
- **CORS**: `django-cors-headers`
- **Port**: 8000 by default (`http://127.0.0.1:8000/`)

---

## Project Structure (simplified)
```
Contacts/
├── Contacts/                    # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py                  # Routes: '/', '/contacts/...'
│   └── wsgi.py
│
├── contacts_app/                # Main application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                # Contact, ContactMethod
│   ├── views.py                 # API + import/export + bookmark
│   ├── urls.py                  # /contacts/ endpoints
│   ├── templates/
│   │   └── index.html           # Single-page app UI
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/script.js
│   └── migrations/
│       ├── 0001_initial.py
│       ├── 0002_contact_bookmarked.py
│       └── 0003_... + 0004_... # Multiple contact methods
│
├── manage.py
├── requirements.txt
├── README.md
└── LICENSE---
```
## Data Model

### `Contact`

- `id` *(int, PK)*
- `name` *(string)*
- `bookmarked` *(bool, default `False`)*

### `ContactMethod`

- `id` *(int, PK)*
- `contact` *(FK → Contact, related name `contact_methods`)*
- `method_type` *(choice: `phone`, `email`, `social_media`, `address`)*
- `label` *(optional string, e.g. "Work", "Home")*
- `value` *(text, e.g. phone number, email address, URL, or postal address)*
- `is_primary` *(bool, default `False`)*  
  When a method is marked primary, other methods of the same type for that contact are automatically unmarked.

---

## API Overview

Base path for the API: **`/contacts/`**

### Contacts

- **GET** `/contacts/`  
  Returns list of all contacts with methods.

- **POST** `/contacts/`  
  Create a contact with methods.

  Example body:

 
  {
    "name": "Freddy Tao",
    "bookmarked": true,
    "contact_methods": [
      {
        "method_type": "phone",
        "label": "Work",
        "value": "05925588",
        "is_primary": false
      },
      {
        "method_type": "social_media",
        "label": "Instagram",
        "value": "freddy_ig",
        "is_primary": true
      }
    ]
  }
  - **GET** `/contacts/<id>/`  
  Get details for a single contact.

- **PUT** `/contacts/<id>/`  
  Update name, bookmark flag, and **replace** the contact’s methods with the provided list.

 
  {
    "name": "Freddy Tao",
    "bookmarked": false,
    "contact_methods": [ ... ]
  }
  - **DELETE** `/contacts/<id>/`  
  Delete a contact.

### Bookmark

- **POST** `/contacts/<id>/bookmark/`  
  Toggle bookmark status for a contact.

### Contact Methods (optional, lower-level)

- **GET** `/contacts/<id>/methods/`
- **POST** `/contacts/<id>/methods/`
- **PUT** `/contacts/<id>/methods/<method_id>/`
- **DELETE** `/contacts/<id>/methods/<method_id>/`

(Usually the frontend uses the main contact endpoints instead.)

---

## Excel Import / Export

### Export

- **GET** `/contacts/export/`
- Returns an Excel file `contacts_export.xlsx` with columns:

  - `Name`
  - `Bookmarked` (`Yes` / `No`)
  - `Phone`
  - `Email`
  - `Social Media`
  - `Address`

Each cell for a method type may contain multiple values separated by `;`.  
Format for each value:

<value> (Label) [Primary]Examples:

- `123@gmail.com (Work) [Primary]`
- `555-1234 (Home); 555-5678 (Work) [Primary]`

### Import

- **POST** `/contacts/import/` with form-data:
  - `file`: Excel file (`.xlsx` or `.xls`)

Requirements:

- Must have a `Name` column.
- Other columns (`Bookmarked`, `Phone`, `Email`, `Social Media`, `Address`) are optional but recommended.
- Same text format as the export for labels and `[Primary]`.

The server responds with:

{
  "message": "Successfully imported 3 contact(s)",
  "imported": 3,
  "skipped": 1,
  "errors": [
    "Row 5: Name is required"
  ]
}---

## Setup Instructions

### 1. Clone and enter the project

git clone <your-repo-url> Contacts
cd Contacts### 2. Create and activate a virtual environment

python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate### 3. Install dependencies

pip install -r requirements.txt### 4. Apply migrations

python3 manage.py migrate(If you change models, run `python3 manage.py makemigrations` first.)

### 5. Run the development server

python3 manage.py runserverOpen the app at:

- UI: `http://127.0.0.1:8000/`
- API base: `http://127.0.0.1:8000/contacts/`

---

## Frontend Usage (Quick Guide)

- Use the **Add New Contact** form to:
  - Enter a contact name
  - Add one or more contact methods
  - Mark methods as Primary as needed
- Use **+ Add Contact Method** to add extra rows.
- Click the **star** on any contact to bookmark/unbookmark it.
- Use **Export to Excel** to download the full address book.
- Use **Import from Excel** to upload a properly formatted Excel file.

---

## License

This project is licensed under the MIT License.  
See the `LICENSE` file for details.
