"""
Database package initialization
"""

from .db import (
    init_db,
    create_user,
    verify_user,
    get_user_by_username,
    update_password,
    get_all_users,
    delete_user,
    hash_password,
    # User settings functions
    get_user_settings,
    create_user_settings,
    update_user_settings,
    get_user_email_config,
    get_user_emergency_contacts,
    get_user_api_keys
)

__all__ = [
    'init_db',
    'create_user', 
    'verify_user',
    'get_user_by_username',
    'update_password',
    'get_all_users',
    'delete_user',
    'hash_password',
    # User settings
    'get_user_settings',
    'create_user_settings',
    'update_user_settings',
    'get_user_email_config',
    'get_user_emergency_contacts',
    'get_user_api_keys'
]
