"""
PDF Tool - PDF Generation Module
Creates PDF documents using ReportLab
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class PDFTool:
    """
    PDF generation tool using ReportLab.
    Creates professional PDF documents from text content.
    """
    
    def __init__(self):
        """Initialize PDF tool"""
        self.default_font = "Helvetica"
        self.default_font_size = 12
        self.title_font_size = 18
        self.heading_font_size = 14
    
    def create_pdf(
        self,
        content: str,
        output_path: str,
        title: str = None,
        author: str = None,
        include_date: bool = True
    ) -> Dict[str, any]:
        """
        Create a PDF document from text content.
        
        Args:
            content: Text content for the PDF
            output_path: Path to save the PDF
            title: Document title
            author: Document author
            include_date: Whether to include date
            
        Returns:
            Result dictionary
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
            
            # Ensure output directory exists
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            # Create document
            doc = SimpleDocTemplate(
                str(output),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=self.title_font_size,
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=self.heading_font_size,
                spaceBefore=20,
                spaceAfter=10
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontSize=self.default_font_size,
                alignment=TA_JUSTIFY,
                spaceBefore=6,
                spaceAfter=6
            )
            
            # Build content
            story = []
            
            # Add title
            if title:
                story.append(Paragraph(title, title_style))
            
            # Add date
            if include_date:
                date_str = datetime.now().strftime("%B %d, %Y")
                date_style = ParagraphStyle(
                    'DateStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=TA_CENTER,
                    spaceAfter=20
                )
                story.append(Paragraph(date_str, date_style))
            
            # Add author
            if author:
                author_style = ParagraphStyle(
                    'AuthorStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=TA_CENTER,
                    spaceAfter=30
                )
                story.append(Paragraph(f"By: {author}", author_style))
            
            story.append(Spacer(1, 0.5 * inch))
            
            # Process content
            paragraphs = content.split('\n\n')
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # Check if it's a heading (starts with # or all caps)
                if para.startswith('#'):
                    # Markdown-style heading
                    heading_text = para.lstrip('#').strip()
                    story.append(Paragraph(heading_text, heading_style))
                elif para.isupper() and len(para) < 100:
                    # All caps heading
                    story.append(Paragraph(para, heading_style))
                else:
                    # Regular paragraph - escape special characters
                    para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    para = para.replace('\n', '<br/>')
                    story.append(Paragraph(para, body_style))
            
            # Build PDF
            doc.build(story)
            
            return {
                "success": True,
                "message": f"PDF created successfully: {output_path}",
                "file_path": str(output.absolute()),
                "title": title,
                "pages": "1+"  # Actual page count not easily determined before build
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "ReportLab not installed. Run: pip install reportlab"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create PDF: {str(e)}"
            }
    
    def create_report_pdf(
        self,
        title: str,
        sections: Dict[str, str],
        output_path: str,
        author: str = None
    ) -> Dict[str, any]:
        """
        Create a formatted report PDF with sections.
        
        Args:
            title: Report title
            sections: Dictionary of section_title: content
            output_path: Output file path
            author: Report author
            
        Returns:
            Result dictionary
        """
        # Build content with sections
        content_parts = []
        
        for section_title, section_content in sections.items():
            content_parts.append(f"# {section_title}")
            content_parts.append(section_content)
            content_parts.append("")
        
        full_content = "\n\n".join(content_parts)
        
        return self.create_pdf(
            content=full_content,
            output_path=output_path,
            title=title,
            author=author,
            include_date=True
        )
    
    def create_table_pdf(
        self,
        data: List[List[str]],
        headers: List[str],
        output_path: str,
        title: str = None
    ) -> Dict[str, any]:
        """
        Create a PDF with a data table.
        
        Args:
            data: 2D list of table data
            headers: Column headers
            output_path: Output file path
            title: Document title
            
        Returns:
            Result dictionary
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.units import inch
            
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            doc = SimpleDocTemplate(str(output), pagesize=A4)
            styles = getSampleStyleSheet()
            
            story = []
            
            # Add title
            if title:
                story.append(Paragraph(title, styles['Title']))
                story.append(Spacer(1, 0.5 * inch))
            
            # Create table with headers
            table_data = [headers] + data
            
            table = Table(table_data)
            
            # Style the table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(table)
            doc.build(story)
            
            return {
                "success": True,
                "message": f"Table PDF created: {output_path}",
                "file_path": str(output.absolute()),
                "rows": len(data),
                "columns": len(headers)
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "ReportLab not installed. Run: pip install reportlab"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create table PDF: {str(e)}"
            }
    
    def text_to_pdf(self, text_file: str, output_path: str = None) -> Dict[str, any]:
        """
        Convert a text file to PDF.
        
        Args:
            text_file: Path to text file
            output_path: Output PDF path (defaults to same name with .pdf)
            
        Returns:
            Result dictionary
        """
        text_path = Path(text_file)
        
        if not text_path.exists():
            return {"success": False, "error": f"File not found: {text_file}"}
        
        if output_path is None:
            output_path = str(text_path.with_suffix('.pdf'))
        
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.create_pdf(
                content=content,
                output_path=output_path,
                title=text_path.stem.replace('_', ' ').title()
            )
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to convert file: {str(e)}"
            }
    
    def merge_pdfs(self, pdf_files: List[str], output_path: str) -> Dict[str, any]:
        """
        Merge multiple PDF files into one.
        
        Args:
            pdf_files: List of PDF file paths
            output_path: Output file path
            
        Returns:
            Result dictionary
        """
        try:
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            
            for pdf in pdf_files:
                if Path(pdf).exists():
                    merger.append(pdf)
                else:
                    return {"success": False, "error": f"File not found: {pdf}"}
            
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            merger.write(str(output))
            merger.close()
            
            return {
                "success": True,
                "message": f"Merged {len(pdf_files)} PDFs into {output_path}",
                "file_path": str(output.absolute()),
                "merged_count": len(pdf_files)
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "PyPDF2 not installed. Run: pip install PyPDF2"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to merge PDFs: {str(e)}"
            }
