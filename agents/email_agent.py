"""
Email Agent - Automated email composition and sending
Uses LLM to generate professional emails and SMTP to send
"""

from typing import Dict, List, Optional
from .base_agent import BaseAgent, AgentResult


class EmailAgent(BaseAgent):
    """
    Email automation agent that generates and sends emails.
    Combines LLM for content generation with SMTP for delivery.
    """
    
    def __init__(self):
        super().__init__(
            name="Email Automation Agent",
            description="Generate and send professional emails automatically"
        )
        
        from tools.email_tool import EmailTool
        self.email_tool = EmailTool()
    
    def get_capabilities(self) -> List[str]:
        return [
            "Generate professional emails using AI",
            "Send emails via SMTP",
            "Support attachments",
            "Create email drafts",
            "CC and BCC recipients"
        ]
    
    def execute(self, task: str, **kwargs) -> AgentResult:
        """
        Execute email task.
        
        Args:
            task: Task description (e.g., "Send email about meeting to john@example.com")
            **kwargs: Additional parameters
                - to_email: Recipient email
                - subject: Email subject
                - body: Email body (if not using LLM generation)
                - cc: CC recipients
                - attachments: File attachments
                
        Returns:
            AgentResult with email status
        """
        self._start_execution(task)
        result = self._create_result(False, "")
        
        try:
            # Check if this is just a body generation request (not sending)
            task_lower = task.lower()
            is_generate_only = ('generate' in task_lower and 'body' in task_lower) or \
                               ('generate' in task_lower and 'email' in task_lower and 'send' not in task_lower)
            
            if is_generate_only:
                # Just generate email body content, don't send
                result.add_step("generate_body", "started")
                
                llm = self.get_llm()
                
                # Extract subject from task
                subject = ""
                if "subject:" in task_lower or "subject \"" in task_lower:
                    import re
                    subject_match = re.search(r'subject[:\s]*["\']?([^"\']+)["\']?', task, re.IGNORECASE)
                    if subject_match:
                        subject = subject_match.group(1).strip()
                
                # Determine tone
                tone = "professional"
                if any(word in task_lower for word in ["casual", "friendly", "informal"]):
                    tone = "friendly"
                elif any(word in task_lower for word in ["formal", "official"]):
                    tone = "formal"
                
                email_content = llm.generate_email(
                    recipient="Recipient",
                    subject=subject or "Email",
                    purpose=subject or task,
                    tone=tone
                )
                
                body = email_content.get("body", "")
                
                result = self._create_result(
                    True,
                    "Email body generated successfully",
                    data={
                        "body": body,
                        "content": body,
                        "subject": subject,
                        "tone": tone
                    }
                )
                result.add_step("generate_body", "success")
                self._end_execution(result)
                return result
            
            # Parse task to extract parameters
            parsed = self.parse_instruction(task)
            
            # Get email parameters
            to_email = kwargs.get("to_email") or self._extract_email(task)
            subject = kwargs.get("subject")
            body = kwargs.get("body")
            cc = kwargs.get("cc", [])
            attachments = kwargs.get("attachments", [])
            
            # Validate email
            if not to_email:
                result = self._create_result(
                    False,
                    "No recipient email provided",
                    error="Please provide a recipient email address"
                )
                self._end_execution(result)
                return result
            
            if not self.email_tool.validate_email_address(to_email):
                result = self._create_result(
                    False,
                    f"Invalid email format: {to_email}",
                    error="Invalid email format"
                )
                self._end_execution(result)
                return result
            
            result.add_step("validate_input", "success", {"to_email": to_email})
            
            # Generate email content if not provided
            if not body:
                result.add_step("generate_email", "started")
                
                llm = self.get_llm()
                
                # Determine purpose from task
                purpose = task
                if "about" in task.lower():
                    purpose = task.split("about", 1)[1].strip()
                
                # Determine tone
                tone = "professional"
                if any(word in task.lower() for word in ["casual", "friendly", "informal"]):
                    tone = "friendly"
                elif any(word in task.lower() for word in ["formal", "official"]):
                    tone = "formal"
                
                email_content = llm.generate_email(
                    recipient="Recipient",
                    subject=subject or purpose[:50],
                    purpose=purpose,
                    tone=tone
                )
                
                subject = email_content.get("subject", subject or "No Subject")
                body = email_content.get("body", "")
                
                result.add_step("generate_email", "success", {
                    "generated_subject": subject,
                    "body_length": len(body)
                })
            
            # Send the email
            result.add_step("send_email", "started")
            
            send_result = self.email_tool.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                cc=cc,
                attachments=attachments
            )
            
            if send_result.get("success"):
                result = self._create_result(
                    True,
                    f"Email sent successfully to {to_email}",
                    data={
                        "to": to_email,
                        "subject": subject,
                        "body_preview": body[:200] + "..." if len(body) > 200 else body,
                        "cc": cc,
                        "attachments": len(attachments)
                    }
                )
                result.add_step("send_email", "success")
            else:
                # Check if demo mode
                if send_result.get("demo_mode"):
                    result = self._create_result(
                        True,
                        send_result.get("message", "Email prepared (SMTP not configured)"),
                        data={
                            "to": to_email,
                            "subject": subject,
                            "body": body,
                            "demo_mode": True
                        }
                    )
                    result.add_step("send_email", "demo_mode")
                else:
                    result = self._create_result(
                        False,
                        "Failed to send email",
                        error=send_result.get("error", "Unknown error")
                    )
                    result.add_step("send_email", "failed", {"error": send_result.get("error")})
            
        except Exception as e:
            result = self._create_result(
                False,
                f"Email agent error: {str(e)}",
                error=str(e)
            )
        
        self._end_execution(result)
        return result
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        import re
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def create_draft(self, to_email: str, purpose: str) -> AgentResult:
        """Create an email draft without sending"""
        self._start_execution(f"Create draft for {to_email}")
        
        try:
            llm = self.get_llm()
            email_content = llm.generate_email(
                recipient="Recipient",
                subject=purpose,
                purpose=purpose,
                tone="professional"
            )
            
            draft_result = self.email_tool.create_draft(
                to_email=to_email,
                subject=email_content["subject"],
                body=email_content["body"]
            )
            
            result = self._create_result(
                draft_result.get("success", False),
                draft_result.get("message", "Draft created"),
                data=draft_result
            )
            
        except Exception as e:
            result = self._create_result(
                False,
                f"Failed to create draft: {str(e)}",
                error=str(e)
            )
        
        self._end_execution(result)
        return result
