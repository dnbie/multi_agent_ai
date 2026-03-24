"""
Authentication module for Streamlit app
Handles login, signup, and session management
"""

import streamlit as st
from database.db import verify_user, create_user, get_user_by_username


def show_login_page():
    """Display the login/signup page"""
    
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .login-header {
            text-align: center;
            color: #1f77b4;
            margin-bottom: 2rem;
        }
        .login-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .login-header p {
            color: #666;
            font-size: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-header"><h1>🤖 Agent X</h1><p>Task Automation System</p></div>', unsafe_allow_html=True)
        
        # Tabs for Login and Sign Up
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            login_form()
        
        with tab2:
            signup_form()


def login_form():
    """Display login form"""
    with st.form("login_form", clear_on_submit=False):
        st.subheader("Welcome Back!")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        remember_me = st.checkbox("Remember me")
        
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password!")
                return
            
            # Verify user credentials
            user = verify_user(username, password)
            
            if user:
                # Set session state for logged in user
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.username = user['username']
                st.success(f"Welcome back, {user['full_name'] or user['username']}!")
                st.rerun()
            else:
                st.error("Invalid username or password!")
    
    # Show default credentials hint
    st.info("**Demo Credentials:**\n- Username: `admin` | Password: `admin123`\n- Username: `user` | Password: `user123`")


def signup_form():
    """Display signup form"""
    # Initialize session state for form fields to preserve values on validation error
    if "signup_full_name" not in st.session_state:
        st.session_state.signup_full_name = ""
    if "signup_email" not in st.session_state:
        st.session_state.signup_email = ""
    if "signup_username" not in st.session_state:
        st.session_state.signup_username = ""
    
    with st.form("signup_form", clear_on_submit=False):
        st.subheader("Create Account")
        
        full_name = st.text_input("Full Name", value=st.session_state.signup_full_name, placeholder="Enter your full name", key="signup_name_input")
        email = st.text_input("Email", value=st.session_state.signup_email, placeholder="Enter your email", key="signup_email_input")
        username = st.text_input("Username", value=st.session_state.signup_username, placeholder="Choose a username", key="signup_user_input")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        submit = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submit:
            # Save current values to session state
            st.session_state.signup_full_name = full_name
            st.session_state.signup_email = email
            st.session_state.signup_username = username
            
            # Validation
            if not username or not password:
                st.error("Username and password are required!")
                return
            
            if len(username) < 3:
                st.error("Username must be at least 3 characters!")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters!")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match!")
                return
            
            # Check if username already exists
            if get_user_by_username(username):
                st.error("Username already exists! Please choose another.")
                return
            
            # Create user
            success = create_user(username, password, email, full_name)
            
            if success:
                # Clear form state on success
                st.session_state.signup_full_name = ""
                st.session_state.signup_email = ""
                st.session_state.signup_username = ""
                st.success("Account created successfully! Please login.")
            else:
                st.error("Failed to create account. Please try again.")


def logout():
    """Logout the current user"""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.username = None
    # Clear other session states
    for key in list(st.session_state.keys()):
        if key not in ['logged_in', 'user', 'username']:
            del st.session_state[key]


def is_logged_in() -> bool:
    """Check if user is logged in"""
    return st.session_state.get('logged_in', False)


def get_current_user() -> dict:
    """Get current logged in user"""
    return st.session_state.get('user', None)


def require_auth():
    """
    Decorator/Function to require authentication
    Returns True if authenticated, False otherwise
    """
    if not is_logged_in():
        show_login_page()
        return False
    return True


def show_user_info_sidebar():
    """Display user info in sidebar"""
    if is_logged_in():
        user = get_current_user()
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 {user['username']}**")
            if user.get('email'):
                st.caption(f"📧 {user['email']}")
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
