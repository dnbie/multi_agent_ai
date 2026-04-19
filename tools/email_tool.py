"""
Email Tool - SMTP Email Operations
Handles sending emails using SMTP protocol
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
from pathlib import Path


class EmailTool:
    """
    Email tool for sending emails via SMTP.
    Supports Gmail, Outlook, and other SMTP servers.
    """
    
    def __init__(
        self,
        smtp_server: str = None,
        smtp_port: int = None,
        email_address: str = None,
        email_password: str = None
    ):
        """
        Initialize email tool with SMTP credentials.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port (usually 587 for TLS)
            email_address: Sender email address
            email_password: Email password or app password
        """
        from config import get_email_config

        # Get email config from environment variables
        config = get_email_config()
        
        self.smtp_server = smtp_server or config["smtp_server"]
        self.smtp_port = smtp_port or config["smtp_port"]
        self.email_address = email_address or config["email_address"]
        self.email_password = email_password or config["email_password"]
        
        self.is_configured = all([
            self.smtp_server,
            self.smtp_port,
            self.email_address,
            self.email_password
        ])
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        cc: List[str] = None,
        bcc: List[str] = None,
        attachments: List[str] = None,
        html: bool = False
    ) -> Dict[str, any]:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of file paths to attach
            html: Whether body is HTML
            
        Returns:
            Result dictionary with success status
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Email not configured. Please set SMTP credentials in .env file.",
                "demo_mode": True,
                "message": f"[DEMO] Would send email to: {to_email}\nSubject: {subject}\nBody: {body[:200]}..."
            }
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Add body
            content_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, content_type))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    self._attach_file(msg, file_path)
            
            # Build recipient list
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, recipients, msg.as_string())
            
            return {
                "success": True,
                "message": f"Email sent successfully to {to_email}",
                "to": to_email,
                "subject": subject
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "error": "Authentication failed. Check email and password (use App Password for Gmail)."
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "error": f"SMTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach a file to the email message"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Attachment not found: {file_path}")
        
        with open(path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {path.name}'
        )
        msg.attach(part)
    
    def send_email_with_llm(
        self,
        to_email: str,
        purpose: str,
        recipient_name: str = "Recipient",
        tone: str = "professional"
    ) -> Dict[str, any]:
        """
        Generate and send email using LLM.
        
        Args:
            to_email: Recipient email
            purpose: Purpose/intent of the email
            recipient_name: Name of recipient
            tone: Email tone
            
        Returns:
            Result with generated email and send status
        """
        from .llm_tool import LLMTool
        
        try:
            llm = LLMTool()
            
            # Generate email content
            email_content = llm.generate_email(
                recipient=recipient_name,
                subject=purpose,
                purpose=purpose,
                tone=tone
            )
            
            # Send the email
            result = self.send_email(
                to_email=to_email,
                subject=email_content["subject"],
                body=email_content["body"]
            )
            
            result["generated_subject"] = email_content["subject"]
            result["generated_body"] = email_content["body"]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate/send email: {str(e)}"
            }
    
    def create_draft(
        self,
        to_email: str,
        subject: str,
        body: str,
        draft_path: str = None
    ) -> Dict[str, any]:
        """
        Create an email draft (save to file).
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            draft_path: Path to save draft
            
        Returns:
            Result with draft file path
        """
        from config import OUTPUT_DIR
        
        if draft_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            draft_path = OUTPUT_DIR / f"email_draft_{timestamp}.txt"
        
        draft_content = f"""TO: {to_email}
SUBJECT: {subject}
DATE: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{body}
"""
        
        try:
            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(draft_content)
            
            return {
                "success": True,
                "message": f"Draft saved to {draft_path}",
                "draft_path": str(draft_path),
                "to": to_email,
                "subject": subject
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save draft: {str(e)}"
            }
    
    def validate_email_address(self, email: str) -> bool:
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_status(self) -> Dict[str, any]:
        """Get email tool configuration status"""
        return {
            "configured": self.is_configured,
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "email_address": self.email_address[:3] + "***" if self.email_address else None
        }
