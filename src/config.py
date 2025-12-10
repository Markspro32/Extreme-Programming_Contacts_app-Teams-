import os

class Config:
    # Database configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URI = os.path.join(BASE_DIR, 'contacts.db')