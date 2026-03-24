"""
User Profile Settings Page
Allows users to configure their personal settings, email credentials, emergency contacts, etc.
"""

import streamlit as st
from database.db import (
    get_user_settings, 
    update_user_settings, 
    get_user_email_config,
    get_user_emergency_contacts,
    get_user_api_keys
)


def render_profile_settings():
    """Render the profile settings page"""
    
    st.markdown("## ⚙️ Profile Settings")
    st.markdown("Configure your personal settings, email credentials, and emergency contacts.")
    st.markdown("---")
    
    # Get current user from session
    user = st.session_state.get('user')
    if not user:
        st.error("Please login to access settings.")
        return
    
    user_id = user['id']
    
    # Load current settings
    current_settings = get_user_settings(user_id) or {}
    email_config = get_user_email_config(user_id)
    emergency_info = get_user_emergency_contacts(user_id)
    api_keys = get_user_api_keys(user_id)
    
    # Create tabs for different settings categories
    tab1, tab2, tab3, tab4 = st.tabs([
        "📧 Email Settings", 
        "🚨 Emergency Contacts", 
        "👤 Personal Info",
        "🔑 API Keys"
    ])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EMAIL SETTINGS TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### Gmail / Email Configuration")
        st.info("Configure your email settings to send emails through the Email Agent. For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833).")
        
        with st.form("email_settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                smtp_server = st.text_input(
                    "SMTP Server",
                    value=email_config.get('smtp_server', 'smtp.gmail.com'),
                    help="For Gmail: smtp.gmail.com"
                )
                email_address = st.text_input(
                    "Email Address",
                    value=email_config.get('email_address', ''),
                    placeholder="your.email@gmail.com"
                )
            
            with col2:
                smtp_port = st.number_input(
                    "SMTP Port",
                    value=email_config.get('smtp_port', 587),
                    min_value=1,
                    max_value=65535,
                    help="For Gmail TLS: 587"
                )
                email_password = st.text_input(
                    "Email Password / App Password",
                    type="password",
                    value=email_config.get('email_password', ''),
                    help="For Gmail, use App Password (16 characters)"
                )
            
            submit_email = st.form_submit_button("💾 Save Email Settings", use_container_width=True)
            
            if submit_email:
                update_user_settings(user_id, {
                    'smtp_server': smtp_server,
                    'smtp_port': smtp_port,
                    'email_address': email_address,
                    'email_password': email_password
                })
                st.success("✅ Email settings saved successfully!")
                st.rerun()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EMERGENCY CONTACTS TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### Emergency Contact Information")
        st.info("These contacts will be used by the Emergency Agent in case of emergencies.")
        
        with st.form("emergency_settings_form"):
            st.markdown("#### Primary Emergency Contact")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                emergency_name = st.text_input(
                    "Contact Name",
                    value=emergency_info['primary'].get('name', ''),
                    placeholder="John Doe"
                )
            with col2:
                emergency_phone = st.text_input(
                    "Phone Number",
                    value=emergency_info['primary'].get('phone', ''),
                    placeholder="+91 9876543210"
                )
            with col3:
                emergency_relation = st.selectbox(
                    "Relationship",
                    options=["", "Spouse", "Parent", "Sibling", "Child", "Friend", "Other"],
                    index=["", "Spouse", "Parent", "Sibling", "Child", "Friend", "Other"].index(
                        emergency_info['primary'].get('relation', '') or ""
                    ) if emergency_info['primary'].get('relation', '') in ["", "Spouse", "Parent", "Sibling", "Child", "Friend", "Other"] else 0
                )
            
            st.markdown("#### Secondary Emergency Contact")
            col1, col2 = st.columns(2)
            
            with col1:
                secondary_name = st.text_input(
                    "Secondary Contact Name",
                    value=emergency_info['secondary'].get('name', ''),
                    placeholder="Jane Doe"
                )
            with col2:
                secondary_phone = st.text_input(
                    "Secondary Phone",
                    value=emergency_info['secondary'].get('phone', ''),
                    placeholder="+91 9876543211"
                )
            
            st.markdown("#### Medical Information")
            col1, col2 = st.columns(2)
            
            with col1:
                blood_group = st.selectbox(
                    "Blood Group",
                    options=["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                    index=["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(
                        emergency_info.get('blood_group', '') or ""
                    ) if emergency_info.get('blood_group', '') in ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] else 0
                )
                preferred_hospital = st.text_input(
                    "Preferred Hospital",
                    value=emergency_info.get('preferred_hospital', ''),
                    placeholder="Apollo Hospital"
                )
            
            with col2:
                medical_conditions = st.text_area(
                    "Medical Conditions / Allergies",
                    value=emergency_info.get('medical_conditions', ''),
                    placeholder="Diabetes, Penicillin allergy, etc.",
                    height=100
                )
            
            home_address = st.text_area(
                "Home Address",
                value=emergency_info.get('home_address', ''),
                placeholder="123, Main Street, City, State - PIN",
                height=80
            )
            
            submit_emergency = st.form_submit_button("💾 Save Emergency Settings", use_container_width=True)
            
            if submit_emergency:
                update_user_settings(user_id, {
                    'emergency_contact_name': emergency_name,
                    'emergency_contact_phone': emergency_phone,
                    'emergency_contact_relation': emergency_relation,
                    'secondary_emergency_name': secondary_name,
                    'secondary_emergency_phone': secondary_phone,
                    'blood_group': blood_group,
                    'medical_conditions': medical_conditions,
                    'preferred_hospital': preferred_hospital,
                    'home_address': home_address
                })
                st.success("✅ Emergency contact settings saved successfully!")
                st.rerun()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PERSONAL INFO TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### Personal Information")
        
        with st.form("personal_info_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                phone_number = st.text_input(
                    "Phone Number",
                    value=current_settings.get('phone_number', ''),
                    placeholder="+91 9876543210"
                )
                city = st.text_input(
                    "City",
                    value=current_settings.get('city', '') or emergency_info.get('city', ''),
                    placeholder="Chennai",
                    help="Used for weather, emergency services, etc."
                )
            
            with col2:
                default_provider = st.selectbox(
                    "Default LLM Provider",
                    options=["gemini", "openai"],
                    index=["gemini", "openai"].index(
                        current_settings.get('default_llm_provider', 'gemini') or 'gemini'
                    ),
                    format_func=lambda x: "Google Gemini" if x == "gemini" else "OpenAI"
                )
                
                if default_provider == "gemini":
                    model_options = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro", "gemini-2.0-flash", "gemini-pro"]
                else:
                    model_options = ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"]
                
                current_model = current_settings.get('default_model', model_options[0])
                if current_model not in model_options:
                    current_model = model_options[0]
                
                default_model = st.selectbox(
                    "Default Model",
                    options=model_options,
                    index=model_options.index(current_model)
                )
            
            submit_personal = st.form_submit_button("💾 Save Personal Info", use_container_width=True)
            
            if submit_personal:
                update_user_settings(user_id, {
                    'phone_number': phone_number,
                    'city': city,
                    'default_llm_provider': default_provider,
                    'default_model': default_model
                })
                st.success("✅ Personal information saved successfully!")
                st.rerun()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # API KEYS TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### API Keys (Optional)")
        st.warning("⚠️ If left empty, the system will use default API keys from the server configuration.")
        
        with st.form("api_keys_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                google_api_key = st.text_input(
                    "Google Gemini API Key",
                    type="password",
                    value=api_keys.get('google_api_key', ''),
                    help="Get from: https://makersuite.google.com/app/apikey"
                )
                weather_api_key = st.text_input(
                    "OpenWeather API Key",
                    type="password",
                    value=api_keys.get('weather_api_key', ''),
                    help="Get from: https://openweathermap.org/api"
                )
            
            with col2:
                openai_api_key = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    value=api_keys.get('openai_api_key', ''),
                    help="Get from: https://platform.openai.com/api-keys"
                )
                news_api_key = st.text_input(
                    "News API Key",
                    type="password",
                    value=api_keys.get('news_api_key', ''),
                    help="Get from: https://newsapi.org"
                )
            
            submit_api = st.form_submit_button("💾 Save API Keys", use_container_width=True)
            
            if submit_api:
                update_user_settings(user_id, {
                    'google_api_key': google_api_key,
                    'openai_api_key': openai_api_key,
                    'weather_api_key': weather_api_key,
                    'news_api_key': news_api_key
                })
                st.success("✅ API keys saved successfully!")
                st.rerun()
    
    # Show current settings summary
    st.markdown("---")
    with st.expander("📋 Current Settings Summary", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Email Configuration**")
            st.write(f"- Server: `{email_config.get('smtp_server', 'Not set')}`")
            st.write(f"- Email: `{email_config.get('email_address', 'Not set') or 'Not set'}`")
            st.write(f"- Password: `{'••••••••' if email_config.get('email_password') else 'Not set'}`")
        
        with col2:
            st.markdown("**Emergency Contact**")
            st.write(f"- Primary: `{emergency_info['primary'].get('name', 'Not set') or 'Not set'}`")
            st.write(f"- Phone: `{emergency_info['primary'].get('phone', 'Not set') or 'Not set'}`")
            st.write(f"- Blood Group: `{emergency_info.get('blood_group', 'Not set') or 'Not set'}`")
