import sqlite3
from config import Config

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(Config.DATABASE_URI)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the contacts table"""
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def get_all_contacts():
    """Get all contacts from the database"""
    conn = get_db_connection()
    contacts = conn.execute('SELECT * FROM contacts').fetchall()
    conn.close()
    return [dict(contact) for contact in contacts]

def get_contact_by_id(contact_id):
    """Get a single contact by ID"""
    conn = get_db_connection()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    conn.close()
    return dict(contact) if contact else None

def add_contact(name, phone):
    """Add a new contact to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO contacts (name, phone) VALUES (?, ?)', (name, phone))
    conn.commit()
    contact_id = cursor.lastrowid
    conn.close()
    return contact_id

def update_contact(contact_id, name, phone):
    """Update an existing contact"""
    conn = get_db_connection()
    conn.execute('UPDATE contacts SET name = ?, phone = ? WHERE id = ?', 
                 (name, phone, contact_id))
    conn.commit()
    conn.close()
    return True

def delete_contact(contact_id):
    """Delete a contact from the database"""
    conn = get_db_connection()
    conn.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    conn.commit()
    conn.close()
    return True