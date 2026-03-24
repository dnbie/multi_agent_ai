"""
Configuration Module for Agent X Task Automation System
Loads environment variables and provides system-wide settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = OUTPUT_DIR / "reports"
SUMMARIES_DIR = OUTPUT_DIR / "summaries"
ORGANIZED_DIR = OUTPUT_DIR / "organized"

# Create directories if they don't exist
for directory in [DATA_DIR, OUTPUT_DIR, LOGS_DIR, REPORTS_DIR, SUMMARIES_DIR, ORGANIZED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" or "openai"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Email SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# LLM Settings
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2048

# Agent Settings
AGENT_TIMEOUT = 300  # seconds
MAX_RETRY_ATTEMPTS = 3

# Logging Settings
LOG_FILE = LOGS_DIR / "actions.json"
LOG_FORMAT = "json"  # "json" or "txt"

# Available Agents
AVAILABLE_AGENTS = {
    "email": "Email Automation Agent",
    "report": "Report Generation Agent",
    "flight": "Flight Search Agent",
    "bus": "Bus Route Agent",
    "train": "Train Booking Agent",
    "file_organizer": "File Organizer Agent",
    "browser": "Browser Agent",
    "weather": "Weather Agent",
    "news": "News Agent",
    "reminder": "Reminder Agent",
    "emergency": "Emergency Agent"
}

# Tool Descriptions for Agent Selection
TOOL_DESCRIPTIONS = {
    "email_tool": "Send emails using SMTP",
    "file_tool": "Read and write files",
    "pdf_tool": "Generate PDF documents",
    "llm_tool": "Generate text using AI",
    "flight_api": "Search flight information",
    "bus_api": "Search bus routes",
    "data_tool": "Analyze data files"
}

def get_llm_config():
    """Get LLM configuration based on provider"""
    if LLM_PROVIDER == "gemini":
        return {
            "provider": "gemini",
            "api_key": GOOGLE_API_KEY,
            "model": "gemini-pro"
        }
    else:
        return {
            "provider": "openai",
            "api_key": OPENAI_API_KEY,
            "model": "gpt-3.5-turbo"
        }

def get_email_config(user_id=None):
    """
    Get email configuration.
    If user_id is provided, returns user-specific settings.
    Falls back to environment variables if user settings are empty.
    """
    # Try to get user-specific settings
    if user_id:
        try:
            from database.db import get_user_email_config
            user_config = get_user_email_config(user_id)
            
            # Return user config if email is set, otherwise fall back to defaults
            if user_config.get('email_address'):
                return user_config
        except Exception:
            pass
    
    # Fall back to environment variables
    return {
        "smtp_server": SMTP_SERVER,
        "smtp_port": SMTP_PORT,
        "email_address": EMAIL_ADDRESS,
        "email_password": EMAIL_PASSWORD
    }


def get_user_email_config_from_session():
    """Get email config for currently logged-in user from Streamlit session"""
    try:
        import streamlit as st
        user = st.session_state.get('user')
        if user:
            return get_email_config(user['id'])
    except Exception:
        pass
    return get_email_config()


def get_user_emergency_info_from_session():
    """Get emergency contact info for currently logged-in user"""
    try:
        import streamlit as st
        from database.db import get_user_emergency_contacts
        user = st.session_state.get('user')
        if user:
            return get_user_emergency_contacts(user['id'])
    except Exception:
        pass
    return None
