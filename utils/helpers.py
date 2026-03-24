"""
Helper Utilities
Common utility functions used across the system
"""

import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path


def format_timestamp(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string.
    
    Args:
        dt: Datetime object (defaults to now)
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    Sanitize a filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        replacement: Character to replace invalid chars with
        
    Returns:
        Sanitized filename
    """
    # Characters not allowed in Windows filenames
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, replacement, filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Limit length
    max_length = 200
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:max_length - len(ext)] + ext
    
    return sanitized


def extract_email_parts(email_text: str) -> Dict[str, str]:
    """
    Extract parts from an email text.
    
    Args:
        email_text: Raw email content
        
    Returns:
        Dictionary with subject, body, from, to fields
    """
    parts = {
        "subject": "",
        "body": "",
        "from": "",
        "to": ""
    }
    
    lines = email_text.strip().split('\n')
    body_start = 0
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if line_lower.startswith("subject:"):
            parts["subject"] = line[8:].strip()
        elif line_lower.startswith("from:"):
            parts["from"] = line[5:].strip()
        elif line_lower.startswith("to:"):
            parts["to"] = line[3:].strip()
        elif line.strip() == "":
            body_start = i + 1
            break
    
    if body_start > 0:
        parts["body"] = '\n'.join(lines[body_start:])
    else:
        parts["body"] = email_text
    
    return parts


def parse_task_instruction(instruction: str) -> Dict[str, any]:
    """
    Parse a natural language task instruction to extract key components.
    
    Args:
        instruction: Natural language instruction
        
    Returns:
        Parsed instruction with identified components
    """
    instruction_lower = instruction.lower()
    
    parsed = {
        "original": instruction,
        "action": None,
        "target": None,
        "parameters": {}
    }
    
    # Detect action type
    action_keywords = {
        "send": ["send", "email", "mail"],
        "read": ["read", "open", "view", "show"],
        "write": ["write", "save", "create", "generate"],
        "summarize": ["summarize", "summary", "summarise"],
        "analyze": ["analyze", "analyse", "analysis"],
        "search": ["search", "find", "look for", "lookup"],
        "organize": ["organize", "organise", "sort", "arrange"],
        "move": ["move", "transfer"],
        "rename": ["rename"],
        "delete": ["delete", "remove"]
    }
    
    for action, keywords in action_keywords.items():
        if any(kw in instruction_lower for kw in keywords):
            parsed["action"] = action
            break
    
    # Extract email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, instruction)
    if emails:
        parsed["parameters"]["emails"] = emails
    
    # Extract file paths
    file_pattern = r'["\']?([a-zA-Z]:\\[^"\'<>|*?\n]+|[./]?[\w\-./]+\.\w+)["\']?'
    files = re.findall(file_pattern, instruction)
    if files:
        parsed["parameters"]["files"] = files
    
    return parsed


def chunk_text(text: str, max_chunk_size: int = 3000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks for processing.
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            break_point = max(last_period, last_newline)
            
            if break_point > start + max_chunk_size // 2:
                end = break_point + 1
        
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks


def extract_key_info(text: str, info_type: str) -> List[str]:
    """
    Extract specific types of information from text.
    
    Args:
        text: Text to extract from
        info_type: Type of info ('email', 'phone', 'date', 'url')
        
    Returns:
        List of extracted items
    """
    patterns = {
        "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "phone": r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}',
        "date": r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        "url": r'https?://[^\s<>"{}|\\^`\[\]]+'
    }
    
    pattern = patterns.get(info_type, "")
    if not pattern:
        return []
    
    return re.findall(pattern, text)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_file_info(file_path: str) -> Dict:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    
    if not path.exists():
        return {"exists": False, "error": "File not found"}
    
    stat = path.stat()
    
    return {
        "exists": True,
        "name": path.name,
        "extension": path.suffix,
        "size": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir()
    }


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text
