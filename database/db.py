"""
Database module for user authentication and settings
Uses SQLite for storing user credentials and personalized settings
"""

import sqlite3
import hashlib
import json
import os
from pathlib import Path

# Database path - use /tmp on serverless (Vercel), otherwise local
DB_DIR = Path(__file__).parent
if os.environ.get('VERCEL'):
    DB_PATH = Path("/tmp") / "users.db"
else:
    DB_PATH = DB_DIR / "users.db"


def get_connection():
    """Get database connection"""
    return sqlite3.connect(str(DB_PATH))


def init_db():
    """Initialize the database and create users table"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_settings table for personalized configurations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            
            -- Email/Gmail Settings
            smtp_server TEXT DEFAULT 'smtp.gmail.com',
            smtp_port INTEGER DEFAULT 587,
            email_address TEXT,
            email_password TEXT,
            
            -- Emergency Contact Settings
            emergency_contact_name TEXT,
            emergency_contact_phone TEXT,
            emergency_contact_relation TEXT,
            secondary_emergency_name TEXT,
            secondary_emergency_phone TEXT,
            home_address TEXT,
            blood_group TEXT,
            medical_conditions TEXT,
            preferred_hospital TEXT,
            
            -- Personal Info
            phone_number TEXT,
            city TEXT,
            
            -- API Keys (optional user-specific)
            google_api_key TEXT,
            openai_api_key TEXT,
            weather_api_key TEXT,
            news_api_key TEXT,
            
            -- Preferences
            default_llm_provider TEXT DEFAULT 'gemini',
            default_model TEXT DEFAULT 'gemini-1.5-flash',
            
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, password: str, email: str = None, full_name: str = None) -> bool:
    """
    Create a new user in the database
    Returns True if successful, False if user already exists
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password, email, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, hashed_password, email, full_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username already exists
        return False
    finally:
        conn.close()


def verify_user(username: str, password: str) -> dict:
    """
    Verify user credentials
    Returns user data if valid, None if invalid
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    cursor.execute('''
        SELECT id, username, email, full_name, created_at
        FROM users
        WHERE username = ? AND password = ?
    ''', (username, hashed_password))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[3],
            'created_at': user[4]
        }
    return None


def get_user_by_username(username: str) -> dict:
    """Get user by username"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, full_name, created_at
        FROM users
        WHERE username = ?
    ''', (username,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[3],
            'created_at': user[4]
        }
    return None


def update_password(username: str, new_password: str) -> bool:
    """Update user password"""
    conn = get_connection()
    cursor = conn.cursor()
    
    hashed_password = hash_password(new_password)
    cursor.execute('''
        UPDATE users SET password = ?
        WHERE username = ?
    ''', (hashed_password, username))
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0


def get_all_users() -> list:
    """Get all users (admin function)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, full_name, created_at
        FROM users
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    return [{
        'id': user[0],
        'username': user[1],
        'email': user[2],
        'full_name': user[3],
        'created_at': user[4]
    } for user in users]


def delete_user(username: str) -> bool:
    """Delete a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0


# ═══════════════════════════════════════════════════════════════════════════════
# USER SETTINGS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_user_settings(user_id: int) -> dict:
    """Get user settings by user_id"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM user_settings WHERE user_id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        columns = [
            'id', 'user_id', 'smtp_server', 'smtp_port', 'email_address', 'email_password',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'secondary_emergency_name', 'secondary_emergency_phone', 'home_address',
            'blood_group', 'medical_conditions', 'preferred_hospital',
            'phone_number', 'city', 'google_api_key', 'openai_api_key',
            'weather_api_key', 'news_api_key', 'default_llm_provider', 'default_model', 'updated_at'
        ]
        return dict(zip(columns, row))
    return None


def create_user_settings(user_id: int) -> bool:
    """Create default settings for a new user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO user_settings (user_id) VALUES (?)
        ''', (user_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def update_user_settings(user_id: int, settings: dict) -> bool:
    """Update user settings"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if settings exist, create if not
    cursor.execute('SELECT id FROM user_settings WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO user_settings (user_id) VALUES (?)', (user_id,))
    
    # Build dynamic update query
    valid_fields = [
        'smtp_server', 'smtp_port', 'email_address', 'email_password',
        'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
        'secondary_emergency_name', 'secondary_emergency_phone', 'home_address',
        'blood_group', 'medical_conditions', 'preferred_hospital',
        'phone_number', 'city', 'google_api_key', 'openai_api_key',
        'weather_api_key', 'news_api_key', 'default_llm_provider', 'default_model'
    ]
    
    updates = []
    values = []
    for field in valid_fields:
        if field in settings:
            updates.append(f"{field} = ?")
            values.append(settings[field])
    
    if updates:
        values.append(user_id)
        query = f"UPDATE user_settings SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
        cursor.execute(query, values)
    
    conn.commit()
    conn.close()
    return True


def get_user_email_config(user_id: int) -> dict:
    """Get user's email configuration"""
    settings = get_user_settings(user_id)
    if settings:
        return {
            'smtp_server': settings.get('smtp_server') or 'smtp.gmail.com',
            'smtp_port': settings.get('smtp_port') or 587,
            'email_address': settings.get('email_address') or '',
            'email_password': settings.get('email_password') or ''
        }
    return {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'email_address': '',
        'email_password': ''
    }


def get_user_emergency_contacts(user_id: int) -> dict:
    """Get user's emergency contact information"""
    settings = get_user_settings(user_id)
    if settings:
        return {
            'primary': {
                'name': settings.get('emergency_contact_name') or '',
                'phone': settings.get('emergency_contact_phone') or '',
                'relation': settings.get('emergency_contact_relation') or ''
            },
            'secondary': {
                'name': settings.get('secondary_emergency_name') or '',
                'phone': settings.get('secondary_emergency_phone') or ''
            },
            'home_address': settings.get('home_address') or '',
            'blood_group': settings.get('blood_group') or '',
            'medical_conditions': settings.get('medical_conditions') or '',
            'preferred_hospital': settings.get('preferred_hospital') or '',
            'city': settings.get('city') or ''
        }
    return {
        'primary': {'name': '', 'phone': '', 'relation': ''},
        'secondary': {'name': '', 'phone': ''},
        'home_address': '', 'blood_group': '', 'medical_conditions': '',
        'preferred_hospital': '', 'city': ''
    }


def get_user_api_keys(user_id: int) -> dict:
    """Get user's API keys"""
    settings = get_user_settings(user_id)
    if settings:
        return {
            'google_api_key': settings.get('google_api_key') or '',
            'openai_api_key': settings.get('openai_api_key') or '',
            'weather_api_key': settings.get('weather_api_key') or '',
            'news_api_key': settings.get('news_api_key') or ''
        }
    return {
        'google_api_key': '', 'openai_api_key': '',
        'weather_api_key': '', 'news_api_key': ''
    }


# Initialize database on module import
init_db()

# Create a default admin user if no users exist
if not get_all_users():
    create_user("admin", "admin123", "admin@example.com", "Administrator")
    create_user("user", "user123", "user@example.com", "Test User")
    print("Default users created: admin/admin123, user/user123")
