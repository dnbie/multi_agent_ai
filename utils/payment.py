"""
Fake Payment Module for Agent X
Simulates a payment gateway for ticket booking agents (Flight, Bus, Train)
"""

import streamlit as st
import random
import string
from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import BytesIO

# PDF Generation imports
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def generate_pdf_ticket(booking_type: str, booking_id: str, transaction_id: str, 
                        amount: float, booking_details: dict = None) -> bytes:
    """
    Generate a PDF e-ticket using reportlab
    
    Returns:
        PDF content as bytes
    """
    if not PDF_AVAILABLE:
        # Fallback to text if reportlab not available
        content = f"""
===================================
AGENT X - E-TICKET
===================================

Booking ID: {booking_id}
Transaction ID: {transaction_id}

Booking Type: {booking_type.upper()}
Amount Paid: Rs. {amount:,.2f}
Payment Status: CONFIRMED
Date: {datetime.now().strftime('%d %b %Y, %I:%M %p')}

{chr(10).join([f'{k}: {v}' for k, v in (booking_details or {}).items()])}

===================================
Thank you for booking with Agent X!
===================================
"""
        return content.encode('utf-8')
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceBefore=15,
        spaceAfter=10
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#444444'),
        spaceAfter=5
    )
    success_style = ParagraphStyle(
        'Success',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#28a745'),
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=10
    )
    
    # Build content
    content = []
    
    # Header
    content.append(Paragraph("🎫 AGENT X", title_style))
    content.append(Paragraph(f"{booking_type.upper()} E-TICKET", subtitle_style))
    content.append(Spacer(1, 10))
    
    # Success badge
    content.append(Paragraph("✅ BOOKING CONFIRMED", success_style))
    content.append(Spacer(1, 20))
    
    # Booking Info Table
    booking_data = [
        ['Booking ID', booking_id],
        ['Transaction ID', transaction_id],
        ['Amount Paid', f'₹{amount:,.2f}'],
        ['Payment Status', 'CONFIRMED'],
        ['Booking Date', datetime.now().strftime('%d %b %Y, %I:%M %p')],
    ]
    
    booking_table = Table(booking_data, colWidths=[2.5*inch, 4*inch])
    booking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    content.append(booking_table)
    content.append(Spacer(1, 25))
    
    # Journey Details
    if booking_details:
        content.append(Paragraph(f"{booking_type.upper()} DETAILS", heading_style))
        
        details_data = [[k, str(v)] for k, v in booking_details.items() if k.lower() != 'fare']
        
        if details_data:
            details_table = Table(details_data, colWidths=[2.5*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            content.append(details_table)
    
    content.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceBefore=20
    )
    content.append(Paragraph("─" * 60, footer_style))
    content.append(Paragraph("Thank you for booking with Agent X!", footer_style))
    content.append(Paragraph("Please carry this e-ticket at the time of boarding.", footer_style))
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}", footer_style))
    
    # Build PDF
    doc.build(content)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def generate_transaction_id():
    """Generate a fake transaction ID"""
    prefix = "TXN"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{timestamp}{random_suffix}"


def generate_booking_id(booking_type="TKT"):
    """Generate a fake booking ID"""
    prefixes = {
        "flight": "FLT",
        "train": "TRN",
        "bus": "BUS",
        "ticket": "TKT"
    }
    prefix = prefixes.get(booking_type.lower(), "TKT")
    random_num = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{random_num}"


def render_payment_form(booking_type: str, amount: float, booking_details: dict = None):
    """
    Render a fake payment form
    
    Args:
        booking_type: Type of booking (flight, train, bus)
        amount: Total amount to pay
        booking_details: Dictionary with booking details to display
    """
    
    st.markdown("---")
    st.markdown("### 💳 Payment Gateway")
    st.info("**Demo Mode:** This is a simulated payment for demonstration purposes. No real payment will be processed.")
    
    # Show booking summary
    if booking_details:
        with st.expander("📋 Booking Summary", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                for key, value in list(booking_details.items())[:5]:
                    st.write(f"**{key}:** {value}")
            with col2:
                for key, value in list(booking_details.items())[5:10]:
                    st.write(f"**{key}:** {value}")
    
    # Amount display
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
        <h2 style="color: white; margin: 0;">Total Amount</h2>
        <h1 style="color: white; margin: 10px 0;">₹{amount:,.2f}</h1>
        <p style="color: #e0e0e0; margin: 0;">Including all taxes & fees</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Payment method selection
    st.markdown("#### Select Payment Method")
    payment_method = st.radio(
        "Choose payment method",
        ["💳 Credit/Debit Card", "🏦 Net Banking", "📱 UPI", "💰 Wallet"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Payment form based on method
    with st.form("payment_form"):
        if "Credit/Debit Card" in payment_method:
            col1, col2 = st.columns(2)
            with col1:
                card_number = st.text_input(
                    "Card Number",
                    placeholder="1234 5678 9012 3456",
                    max_chars=19
                )
                card_holder = st.text_input(
                    "Card Holder Name",
                    placeholder="JOHN DOE"
                )
            with col2:
                col_exp, col_cvv = st.columns(2)
                with col_exp:
                    expiry = st.text_input(
                        "Expiry (MM/YY)",
                        placeholder="12/28",
                        max_chars=5
                    )
                with col_cvv:
                    cvv = st.text_input(
                        "CVV",
                        type="password",
                        placeholder="***",
                        max_chars=4
                    )
        
        elif "Net Banking" in payment_method:
            bank = st.selectbox(
                "Select Your Bank",
                ["-- Select Bank --", "State Bank of India", "HDFC Bank", "ICICI Bank", 
                 "Axis Bank", "Punjab National Bank", "Bank of Baroda", "Kotak Mahindra Bank",
                 "Yes Bank", "IndusInd Bank", "Other"]
            )
        
        elif "UPI" in payment_method:
            upi_id = st.text_input(
                "UPI ID",
                placeholder="yourname@upi"
            )
            st.caption("You'll receive a payment request on your UPI app")
        
        elif "Wallet" in payment_method:
            wallet = st.selectbox(
                "Select Wallet",
                ["-- Select Wallet --", "Paytm", "PhonePe", "Amazon Pay", 
                 "Google Pay", "MobiKwik", "Freecharge"]
            )
        
        # Terms checkbox
        agree = st.checkbox("I agree to the terms and conditions")
        
        # Red Pay button styling
        st.markdown("""
        <style>
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #dc3545 !important;
            color: white !important;
            border: none !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #c82333 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Submit button
        submit_payment = st.form_submit_button(
            f"🔒 Pay ₹{amount:,.2f}",
            use_container_width=True
        )
        
        if submit_payment:
            if not agree:
                st.error("Please agree to the terms and conditions")
            else:
                return True
    
    return False


def send_confirmation_email(
    booking_type: str,
    booking_id: str,
    transaction_id: str,
    amount: float,
    booking_details: dict = None
) -> dict:
    """
    Send a real confirmation email using user's Gmail settings from profile.
    
    Returns:
        dict with 'success' and 'message' keys
    """
    try:
        from config import get_user_email_config_from_session
        
        # Get user email config
        config = get_user_email_config_from_session()
        
        smtp_server = config.get('smtp_server')
        smtp_port = config.get('smtp_port', 587)
        email_address = config.get('email_address')
        email_password = config.get('email_password')
        
        # Check if email is configured
        if not all([smtp_server, email_address, email_password]):
            return {
                "success": False,
                "message": "Email not configured. Please set up your email in Profile Settings."
            }
        
        # Build email content
        ticket_type = booking_type.upper()
        details_html = ""
        details_text = ""
        
        if booking_details:
            details_html = "<table style='width: 100%; border-collapse: collapse;'>"
            for key, value in booking_details.items():
                if key.lower() != 'fare':  # Skip fare, we show amount separately
                    details_html += f"<tr><td style='padding: 8px; border-bottom: 1px solid #eee;'><strong>{key}</strong></td><td style='padding: 8px; border-bottom: 1px solid #eee;'>{value}</td></tr>"
                    details_text += f"{key}: {value}\n"
            details_html += "</table>"
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .success-badge {{ background: #28a745; color: white; padding: 10px 20px; border-radius: 20px; display: inline-block; margin: 10px 0; }}
                .details-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .amount {{ font-size: 32px; color: #667eea; font-weight: bold; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🎫 Agent X</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">{ticket_type} Booking Confirmation</p>
                </div>
                <div class="content">
                    <div style="text-align: center;">
                        <span class="success-badge">✅ Payment Successful</span>
                        <p class="amount">₹{amount:,.2f}</p>
                    </div>
                    
                    <div class="details-box">
                        <h3 style="margin-top: 0; color: #333;">Booking Information</h3>
                        <p><strong>Booking ID:</strong> {booking_id}</p>
                        <p><strong>Transaction ID:</strong> {transaction_id}</p>
                        <p><strong>Date:</strong> {datetime.now().strftime('%d %b %Y, %I:%M %p')}</p>
                        <p><strong>Status:</strong> <span style="color: #28a745;">Confirmed</span></p>
                    </div>
                    
                    <div class="details-box">
                        <h3 style="margin-top: 0; color: #333;">{ticket_type} Details</h3>
                        {details_html}
                    </div>
                    
                    <p style="text-align: center; color: #666;">
                        Please save your Booking ID for future reference.<br>
                        Show this email at the time of boarding.
                    </p>
                </div>
                <div class="footer">
                    <p>Thank you for booking with Agent X!</p>
                    <p>This is an automated confirmation email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_body = f"""
        AGENT X - {ticket_type} BOOKING CONFIRMATION
        ============================================
        
        Payment Successful!
        Amount: Rs. {amount:,.2f}
        
        Booking Information:
        - Booking ID: {booking_id}
        - Transaction ID: {transaction_id}
        - Date: {datetime.now().strftime('%d %b %Y, %I:%M %p')}
        - Status: Confirmed
        
        {ticket_type} Details:
        {details_text}
        
        Please save your Booking ID for future reference.
        Show this email at the time of boarding.
        
        Thank you for booking with Agent X!
        """
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🎫 Booking Confirmed - {booking_id} | Agent X {ticket_type}"
        msg["From"] = email_address
        msg["To"] = email_address  # Send to self
        
        # Attach both plain text and HTML
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(email_address, email_password)
            server.sendmail(email_address, email_address, msg.as_string())
        
        return {
            "success": True,
            "message": f"Confirmation email sent to {email_address}"
        }
        
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "Email authentication failed. Please check your email settings in Profile Settings. For Gmail, use an App Password."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }


def show_payment_success(booking_type: str, amount: float, booking_details: dict = None):
    """Show payment success screen with booking confirmation"""
    
    transaction_id = generate_transaction_id()
    booking_id = generate_booking_id(booking_type)
    
    # Send confirmation email
    email_result = send_confirmation_email(
        booking_type=booking_type,
        booking_id=booking_id,
        transaction_id=transaction_id,
        amount=amount,
        booking_details=booking_details
    )
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0;">
        <h1 style="color: white; margin: 0;">✅ Payment Successful!</h1>
        <p style="color: #e0e0e0; font-size: 18px; margin: 10px 0;">
            Your booking has been confirmed
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Booking details card
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎫 Booking Details")
        st.markdown(f"""
        - **Booking ID:** `{booking_id}`
        - **Transaction ID:** `{transaction_id}`
        - **Amount Paid:** ₹{amount:,.2f}
        - **Payment Status:** ✅ Confirmed
        - **Date:** {datetime.now().strftime('%d %b %Y, %I:%M %p')}
        """)
    
    with col2:
        st.markdown("#### 📧 Email Confirmation")
        if email_result["success"]:
            st.success(f"""
            ✅ **Email Sent Successfully!**
            
            {email_result['message']}
            
            Please save your Booking ID for future reference.
            """)
        else:
            st.warning(f"""
            ⚠️ **Email Not Sent**
            
            {email_result['message']}
            
            Please save your Booking ID: `{booking_id}`
            """)
    
    # Ticket preview
    if booking_details:
        st.markdown("---")
        st.markdown("#### 🎟️ E-Ticket Preview")
        
        ticket_type = booking_type.upper()
        st.markdown(f"""
        <div style="border: 2px dashed #667eea; padding: 20px; border-radius: 10px; 
                    background: linear-gradient(to right, #f8f9fa, #e9ecef);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="color: #667eea; margin: 0;">Agent X - {ticket_type} TICKET</h3>
                    <p style="color: #666; margin: 5px 0;">Booking ID: {booking_id}</p>
                </div>
                <div style="text-align: right;">
                    <h2 style="color: #28a745; margin: 0;">CONFIRMED</h2>
                </div>
            </div>
            <hr style="border: 1px dashed #ccc;">
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
        """, unsafe_allow_html=True)
        
        for key, value in booking_details.items():
            st.write(f"**{key}:** {value}")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Generate PDF E-Ticket
    pdf_content = generate_pdf_ticket(
        booking_type=booking_type,
        booking_id=booking_id,
        transaction_id=transaction_id,
        amount=amount,
        booking_details=booking_details
    )
    
    st.download_button(
        "📥 Download E-Ticket (PDF)",
        data=pdf_content,
        file_name=f"AgentX_Ticket_{booking_id}.pdf",
        mime="application/pdf"
    )
    
    return booking_id, transaction_id


def render_book_now_button(booking_type: str, selected_option: dict, amount: float):
    """
    Render a 'Book Now' button that triggers payment flow
    
    Args:
        booking_type: flight, train, or bus
        selected_option: Dictionary with selected booking option details
        amount: Total amount for booking
    
    Returns:
        Tuple of (show_payment, booking_details)
    """
    
    # Initialize session states
    if f"show_payment_{booking_type}" not in st.session_state:
        st.session_state[f"show_payment_{booking_type}"] = False
    if f"payment_done_{booking_type}" not in st.session_state:
        st.session_state[f"payment_done_{booking_type}"] = False
    if f"selected_booking_{booking_type}" not in st.session_state:
        st.session_state[f"selected_booking_{booking_type}"] = None
    
    # If payment is done, show success
    if st.session_state[f"payment_done_{booking_type}"]:
        booking_details = st.session_state.get(f"selected_booking_{booking_type}", {})
        show_payment_success(booking_type, amount, booking_details)
        
        if st.button("🔄 Make Another Booking", key=f"new_booking_{booking_type}"):
            st.session_state[f"show_payment_{booking_type}"] = False
            st.session_state[f"payment_done_{booking_type}"] = False
            st.session_state[f"selected_booking_{booking_type}"] = None
            st.rerun()
        return
    
    # Show payment form or book button
    if st.session_state[f"show_payment_{booking_type}"]:
        booking_details = st.session_state.get(f"selected_booking_{booking_type}", {})
        payment_success = render_payment_form(booking_type, amount, booking_details)
        
        if payment_success:
            st.session_state[f"payment_done_{booking_type}"] = True
            st.rerun()
        
        if st.button("← Back to Results", key=f"back_{booking_type}"):
            st.session_state[f"show_payment_{booking_type}"] = False
            st.rerun()
    else:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button(f"🎫 Book Now - ₹{amount:,.0f}", key=f"book_{booking_type}", use_container_width=True):
                st.session_state[f"show_payment_{booking_type}"] = True
                st.session_state[f"selected_booking_{booking_type}"] = selected_option
                st.rerun()
