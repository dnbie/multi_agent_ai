"""
Action Logging System
Records all agent actions with timestamps, task details, and status
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

class ActionLogger:
    """
    Centralized logging system for all agent actions.
    Stores logs in JSON format for easy analysis.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, log_file: str = None):
        """Singleton pattern to ensure single log file"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_file: str = None):
        """Initialize the logger"""
        if self._initialized:
            return
            
        if log_file is None:
            from config import LOG_FILE
            self.log_file = Path(LOG_FILE)
        else:
            self.log_file = Path(log_file)
            
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file if it doesn't exist
        if not self.log_file.exists():
            self._write_logs([])
            
        self._initialized = True
    
    def _read_logs(self) -> List[Dict]:
        """Read existing logs from file"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_logs(self, logs: List[Dict]):
        """Write logs to file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def log_action(
        self,
        agent_name: str,
        task: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Dict:
        """
        Log an agent action.
        
        Args:
            agent_name: Name of the agent performing the action
            task: Description of the task
            status: Status of the action (started, completed, failed)
            details: Additional details about the action
            error: Error message if action failed
            
        Returns:
            The log entry that was created
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "id": self._generate_id(),
            "timestamp": timestamp,
            "agent": agent_name,
            "task": task,
            "status": status,
            "details": details or {},
            "error": error
        }
        
        # Read, append, write
        with self._lock:
            logs = self._read_logs()
            logs.append(log_entry)
            self._write_logs(logs)
        
        return log_entry
    
    def _generate_id(self) -> str:
        """Generate unique log ID"""
        return datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    def get_logs(
        self,
        agent_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve logs with optional filtering.
        
        Args:
            agent_name: Filter by agent name
            status: Filter by status
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        logs = self._read_logs()
        
        # Apply filters
        if agent_name:
            logs = [l for l in logs if l.get("agent") == agent_name]
        if status:
            logs = [l for l in logs if l.get("status") == status]
        
        # Return most recent first, limited
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_session_logs(self, session_start: str) -> List[Dict]:
        """Get logs from a specific session"""
        logs = self._read_logs()
        return [l for l in logs if l["timestamp"] >= session_start]
    
    def clear_logs(self):
        """Clear all logs (use with caution)"""
        with self._lock:
            self._write_logs([])
    
    def export_logs_txt(self, output_file: str) -> str:
        """Export logs to TXT format"""
        logs = self._read_logs()
        
        lines = ["=" * 60, "ACTION LOG EXPORT", "=" * 60, ""]
        
        for log in logs:
            lines.extend([
                f"ID: {log['id']}",
                f"Time: {log['timestamp']}",
                f"Agent: {log['agent']}",
                f"Task: {log['task']}",
                f"Status: {log['status']}",
                f"Details: {json.dumps(log.get('details', {}), indent=2)}",
                "-" * 40,
                ""
            ])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_file
    
    def get_statistics(self) -> Dict:
        """Get logging statistics"""
        logs = self._read_logs()
        
        if not logs:
            return {"total": 0, "by_agent": {}, "by_status": {}}
        
        stats = {
            "total": len(logs),
            "by_agent": {},
            "by_status": {}
        }
        
        for log in logs:
            agent = log.get("agent", "unknown")
            status = log.get("status", "unknown")
            
            stats["by_agent"][agent] = stats["by_agent"].get(agent, 0) + 1
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        return stats


# Global logger instance
logger = ActionLogger()


def log_action(agent_name: str, task: str, status: str, details: Dict = None, error: str = None):
    """Convenience function for logging actions"""
    return logger.log_action(agent_name, task, status, details, error)


def get_logs(agent_name: str = None, status: str = None, limit: int = 100):
    """Convenience function for retrieving logs"""
    return logger.get_logs(agent_name, status, limit)
