"""
Report Generation Agent - Create formatted reports
Generates professional reports in TXT and PDF formats
"""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from .base_agent import BaseAgent, AgentResult


class ReportAgent(BaseAgent):
    """
    Report generation agent that creates formatted reports.
    Uses LLM for content generation and ReportLab for PDF creation.
    """
    
    def __init__(self):
        super().__init__(
            name="Report Generation Agent",
            description="Generate professional reports in TXT and PDF formats"
        )
        
        from tools.file_tool import FileTool
        from tools.pdf_tool import PDFTool
        
        self.file_tool = FileTool()
        self.pdf_tool = PDFTool()
    
    def get_capabilities(self) -> List[str]:
        return [
            "Generate reports from user input",
            "Format text professionally",
            "Save as TXT format",
            "Save as PDF format",
            "Custom report sections"
        ]
    
    def execute(self, task: str, **kwargs) -> AgentResult:
        """
        Execute report generation task.
        
        Args:
            task: Task description (e.g., "Generate report about quarterly sales")
            **kwargs: Additional parameters
                - topic: Report topic
                - sections: Custom sections
                - format: 'txt', 'pdf', or 'both'
                - data: Data to include
                - author: Report author
                
        Returns:
            AgentResult with generated report
        """
        self._start_execution(task)
        result = self._create_result(False, "")
        
        try:
            # Extract parameters
            topic = kwargs.get("topic") or self._extract_topic(task)
            sections = kwargs.get("sections", ["Introduction", "Main Content", "Conclusion"])
            output_format = kwargs.get("format", "both")
            data = kwargs.get("data", "")
            author = kwargs.get("author", "System Generated")
            
            if not topic:
                topic = task  # Use the full task as topic
            
            result.add_step("prepare_report", "started", {"topic": topic})
            
            # Generate report content using LLM
            result.add_step("generate_content", "started")
            
            llm = self.get_llm()
            report_content = llm.generate_report(
                topic=topic,
                data=data if data else None,
                sections=sections if isinstance(sections, list) else None
            )
            
            result.add_step("generate_content", "success", {
                "content_length": len(report_content)
            })
            
            # Prepare output paths
            from config import REPORTS_DIR
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c if c.isalnum() or c in " -_" else "_" for c in topic[:30])
            base_name = f"report_{safe_topic}_{timestamp}"
            
            txt_path = str(REPORTS_DIR / f"{base_name}.txt")
            pdf_path = str(REPORTS_DIR / f"{base_name}.pdf")
            
            saved_files = []
            
            # Save TXT version
            if output_format in ["txt", "both"]:
                result.add_step("save_txt", "started")
                
                txt_content = self._format_txt_report(topic, report_content, author)
                txt_result = self.file_tool.write_file(txt_path, txt_content, overwrite=True)
                
                if txt_result.get("success"):
                    saved_files.append({"format": "TXT", "path": txt_path})
                    result.add_step("save_txt", "success", {"path": txt_path})
                else:
                    result.add_step("save_txt", "failed", {"error": txt_result.get("error")})
            
            # Save PDF version
            if output_format in ["pdf", "both"]:
                result.add_step("save_pdf", "started")
                
                pdf_result = self.pdf_tool.create_pdf(
                    content=report_content,
                    output_path=pdf_path,
                    title=topic.title(),
                    author=author

                )
                
                if pdf_result.get("success"):
                    saved_files.append({"format": "PDF", "path": pdf_path})
                    result.add_step("save_pdf", "success", {"path": pdf_path})
                else:
                    result.add_step("save_pdf", "failed", {"error": pdf_result.get("error")})
            
            # Create final result
            if saved_files:
                result = self._create_result(
                    True,
                    f"Report generated successfully: {topic}",
                    data={
                        "topic": topic,
                        "files": saved_files,
                        "content_preview": report_content[:500] + "..." if len(report_content) > 500 else report_content,
                        "author": author
                    }
                )
            else:
                result = self._create_result(
                    False,
                    "Failed to save report files",
                    error="Could not save to TXT or PDF"
                )
            
        except Exception as e:
            result = self._create_result(
                False,
                f"Report generation error: {str(e)}",
                error=str(e)
            )
        
        self._end_execution(result)
        return result
    
    def generate_content_only(self, task: str, **kwargs) -> dict:
        """
        Generate report content via LLM without saving any files.
        Returns a dict with all the data needed for the preview step.
        """
        topic = kwargs.get("topic") or self._extract_topic(task) or task
        sections = kwargs.get("sections", ["Introduction", "Main Content", "Conclusion"])
        data = kwargs.get("data", "")
        author = kwargs.get("author", "System Generated")
        output_format = kwargs.get("format", "both")

        llm = self.get_llm()
        content = llm.generate_report(
            topic=topic,
            data=data if data else None,
            sections=sections if isinstance(sections, list) else None,
        )
        return {
            "content": content,
            "topic": topic,
            "author": author,
            "output_format": output_format,
            "task": task,
            "kwargs": kwargs,
        }

    def save_report(
        self,
        content: str,
        topic: str,
        author: str = "System Generated",
        output_format: str = "both",
    ) -> AgentResult:
        """
        Save a (possibly user-edited) report to TXT and/or PDF.
        Called after the user approves the preview.
        """
        self._start_execution(f"Save report: {topic}")

        try:
            from config import REPORTS_DIR
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c if c.isalnum() or c in " -_" else "_" for c in topic[:30])
            base_name = f"report_{safe_topic}_{timestamp}"
            txt_path = str(REPORTS_DIR / f"{base_name}.txt")
            pdf_path = str(REPORTS_DIR / f"{base_name}.pdf")

            saved_files = []

            if output_format in ["txt", "both"]:
                result_step = self.file_tool.write_file(
                    txt_path, self._format_txt_report(topic, content, author), overwrite=True
                )
                if result_step.get("success"):
                    saved_files.append({"format": "TXT", "path": txt_path})

            if output_format in ["pdf", "both"]:
                pdf_result = self.pdf_tool.create_pdf(
                    content=content,
                    output_path=pdf_path,
                    title=topic.title(),
                    author=author,
                )
                if pdf_result.get("success"):
                    saved_files.append({"format": "PDF", "path": pdf_path})

            if saved_files:
                result = self._create_result(
                    True,
                    f"Report saved: {topic}",
                    data={
                        "topic": topic,
                        "files": saved_files,
                        "content_preview": content[:500] + "..." if len(content) > 500 else content,
                        "author": author,
                    },
                )
            else:
                result = self._create_result(False, "Failed to save report files", error="Could not save files")

        except Exception as e:
            result = self._create_result(False, f"Save error: {str(e)}", error=str(e))

        self._end_execution(result)
        return result

    def _format_txt_report(self, topic: str, content: str, author: str) -> str:
        """Format report content for TXT file"""
        separator = "=" * 60
        
        return f"""{separator}
REPORT: {topic.upper()}
{separator}

Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}
Author: {author}

{separator}

{content}

{separator}
END OF REPORT
{separator}
"""
    
    def _extract_topic(self, text: str) -> Optional[str]:
        """Extract report topic from task text"""
        text_lower = text.lower()
        
        # Look for common patterns
        patterns = [
            "report about ",
            "report on ",
            "generate report ",
            "create report "
        ]
        
        for pattern in patterns:
            if pattern in text_lower:
                idx = text_lower.find(pattern) + len(pattern)
                return text[idx:].strip()
        
        return None
    
    def generate_from_data(
        self,
        title: str,
        sections: Dict[str, str],
        output_format: str = "both"
    ) -> AgentResult:
        """
        Generate report from structured sections.
        
        Args:
            title: Report title
            sections: Dictionary of section_name: content
            output_format: 'txt', 'pdf', or 'both'
            
        Returns:
            AgentResult
        """
        self._start_execution(f"Generate report: {title}")
        
        try:
            from config import REPORTS_DIR
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            saved_files = []
            
            # Build content
            content_parts = []
            for section, text in sections.items():
                content_parts.append(f"# {section}\n\n{text}\n")
            
            full_content = "\n".join(content_parts)
            
            # Save TXT
            if output_format in ["txt", "both"]:
                txt_path = str(REPORTS_DIR / f"report_{timestamp}.txt")
                txt_content = self._format_txt_report(title, full_content, "System")
                self.file_tool.write_file(txt_path, txt_content, overwrite=True)
                saved_files.append({"format": "TXT", "path": txt_path})
            
            # Save PDF
            if output_format in ["pdf", "both"]:
                pdf_path = str(REPORTS_DIR / f"report_{timestamp}.pdf")
                self.pdf_tool.create_report_pdf(
                    title=title,
                    sections=sections,
                    output_path=pdf_path
                )
                saved_files.append({"format": "PDF", "path": pdf_path})
            
            result = self._create_result(
                True,
                f"Report generated: {title}",
                data={"files": saved_files, "sections": list(sections.keys())}
            )
            
        except Exception as e:
            result = self._create_result(
                False,
                f"Failed to generate report: {str(e)}",
                error=str(e)
            )
        
        self._end_execution(result)
        return result
