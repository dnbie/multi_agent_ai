"""
File Organizer Agent - Organize, rename, and manage files
Intelligent file organization and management
"""

from typing import Dict, List, Optional
from pathlib import Path
from .base_agent import BaseAgent, AgentResult


class FileOrganizerAgent(BaseAgent):
    """
    File organizer agent for organizing and managing files.
    Organizes folders, renames files, and moves files by type.
    """
    
    def __init__(self):
        super().__init__(
            name="File Organizer Agent",
            description="Organize folders, rename files, and move files by type"
        )
        
        from tools.file_tool import FileTool
        self.file_tool = FileTool()
    
    def get_capabilities(self) -> List[str]:
        return [
            "Organize files by type",
            "Batch rename files",
            "Move files between folders",
            "Search for files",
            "Clean up directories"
        ]
    
    def execute(self, task: str, **kwargs) -> AgentResult:
        """
        Execute file management task.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
                - directory: Target directory
                - action: 'organize', 'rename', 'move', 'search', 'cleanup'
                - pattern: Pattern for matching/renaming
                - destination: Destination for moves
                
        Returns:
            AgentResult with operation results
        """
        self._start_execution(task)
        result = self._create_result(False, "")
        
        try:
            # Determine action from task
            task_lower = task.lower()
            action = kwargs.get("action", "auto")
            directory = kwargs.get("directory")
            
            if action == "auto":
                if "organize" in task_lower or "sort" in task_lower or "arrange" in task_lower:
                    action = "organize"
                elif "rename" in task_lower:
                    action = "rename"
                elif "move" in task_lower or "transfer" in task_lower:
                    action = "move"
                elif "search" in task_lower or "find" in task_lower:
                    action = "search"
                elif "clean" in task_lower or "delete" in task_lower:
                    action = "cleanup"
                else:
                    action = "list"  # Default to listing
            
            if not directory:
                directory = self._extract_directory(task)
            
            if not directory and action != "search":
                result = self._create_result(
                    False,
                    "No directory specified",
                    error="Please specify a directory to manage"
                )
                self._end_execution(result)
                return result
            
            # Execute action
            if action == "organize":
                result = self._organize_directory(directory, kwargs)
            elif action == "rename":
                result = self._batch_rename(directory, kwargs)
            elif action == "move":
                result = self._move_files(directory, kwargs)
            elif action == "search":
                result = self._search_files(directory or ".", kwargs.get("query", task))
            elif action == "list":
                result = self._list_directory(directory)
            else:
                result = self._list_directory(directory)
            
        except Exception as e:
            result = self._create_result(
                False,
                f"File management error: {str(e)}",
                error=str(e)
            )
        
        self._end_execution(result)
        return result
    
    def _organize_directory(self, directory: str, kwargs: Dict) -> AgentResult:
        """Organize files by type"""
        result = self._create_result(False, "")
        result.add_step("organize", "started", {"directory": directory})
        
        destination = kwargs.get("destination")
        move_files = kwargs.get("move", False)
        
        organize_result = self.file_tool.organize_by_type(
            source_dir=directory,
            dest_dir=destination,
            move_files=move_files
        )
        
        if organize_result.get("success"):
            organized = organize_result.get("results", {}).get("organized", [])
            
            # Summarize by category
            categories = {}
            for item in organized:
                cat = item.get("category", "other")
                categories[cat] = categories.get(cat, 0) + 1
            
            result = self._create_result(
                True,
                f"Organized {len(organized)} files into categories",
                data={
                    "directory": directory,
                    "destination": organize_result.get("destination"),
                    "files_organized": len(organized),
                    "categories": categories,
                    "details": organized[:20]  # First 20 files
                }
            )
            result.add_step("organize", "success")
        else:
            result = self._create_result(
                False,
                organize_result.get("error", "Organization failed"),
                error=organize_result.get("error")
            )
            result.add_step("organize", "failed")
        
        return result
    
    def _batch_rename(self, directory: str, kwargs: Dict) -> AgentResult:
        """Batch rename files"""
        result = self._create_result(False, "")
        result.add_step("rename", "started")
        
        pattern = kwargs.get("pattern", "")
        replacement = kwargs.get("replacement", "")
        preview = kwargs.get("preview", True)
        
        if not pattern:
            result = self._create_result(
                False,
                "Rename pattern not specified",
                error="Please provide pattern and replacement for renaming"
            )
            return result
        
        rename_result = self.file_tool.batch_rename(
            directory=directory,
            pattern=pattern,
            replacement=replacement,
            preview=preview
        )
        
        if rename_result.get("success"):
            changes = rename_result.get("changes", []) or rename_result.get("applied", [])
            
            result = self._create_result(
                True,
                f"{'Preview: ' if preview else ''}{len(changes)} files would be renamed",
                data={
                    "directory": directory,
                    "pattern": pattern,
                    "replacement": replacement,
                    "preview_mode": preview,
                    "changes": changes
                }
            )
            result.add_step("rename", "success" if not preview else "preview")
        else:
            result = self._create_result(
                False,
                rename_result.get("error", "Rename failed"),
                error=rename_result.get("error")
            )
            result.add_step("rename", "failed")
        
        return result
    
    def _move_files(self, source: str, kwargs: Dict) -> AgentResult:
        """Move files to destination"""
        result = self._create_result(False, "")
        result.add_step("move", "started")
        
        destination = kwargs.get("destination")
        pattern = kwargs.get("pattern", "*")
        
        if not destination:
            result = self._create_result(
                False,
                "Destination not specified",
                error="Please provide destination directory"
            )
            return result
        
        # List files matching pattern
        list_result = self.file_tool.list_directory(source, pattern=pattern)
        
        if not list_result.get("success"):
            return self._create_result(
                False,
                list_result.get("error", "Could not list files"),
                error=list_result.get("error")
            )
        
        # Move each file
        moved = []
        errors = []
        
        for item in list_result.get("items", []):
            if item.get("is_file"):
                move_result = self.file_tool.move_file(
                    item.get("path"),
                    str(Path(destination) / item.get("name"))
                )
                
                if move_result.get("success"):
                    moved.append(item.get("name"))
                else:
                    errors.append({"file": item.get("name"), "error": move_result.get("error")})
        
        result = self._create_result(
            len(errors) == 0,
            f"Moved {len(moved)} files to {destination}",
            data={
                "source": source,
                "destination": destination,
                "moved_count": len(moved),
                "moved_files": moved,
                "errors": errors
            }
        )
        result.add_step("move", "success" if len(errors) == 0 else "partial")
        
        return result
    
    def _search_files(self, directory: str, query: str) -> AgentResult:
        """Search for files"""
        result = self._create_result(False, "")
        result.add_step("search", "started", {"query": query})
        
        search_result = self.file_tool.search_files(
            directory=directory,
            query=query,
            search_content=True
        )
        
        if search_result.get("success"):
            results = search_result.get("results", [])
            
            result = self._create_result(
                True,
                f"Found {len(results)} matching files",
                data={
                    "query": query,
                    "directory": directory,
                    "results_count": len(results),
                    "results": results[:50]  # Limit to 50 results
                }
            )
            result.add_step("search", "success")
        else:
            result = self._create_result(
                False,
                search_result.get("error", "Search failed"),
                error=search_result.get("error")
            )
            result.add_step("search", "failed")
        
        return result
    
    def _list_directory(self, directory: str) -> AgentResult:
        """List directory contents"""
        list_result = self.file_tool.list_directory(directory)
        
        if list_result.get("success"):
            items = list_result.get("items", [])
            
            # Categorize
            files = [i for i in items if i.get("is_file")]
            dirs = [i for i in items if i.get("is_dir")]
            
            return self._create_result(
                True,
                f"Directory contains {len(files)} files and {len(dirs)} folders",
                data={
                    "directory": directory,
                    "total_items": len(items),
                    "files_count": len(files),
                    "folders_count": len(dirs),
                    "items": items
                }
            )
        else:
            return self._create_result(
                False,
                list_result.get("error", "Could not list directory"),
                error=list_result.get("error")
            )
    
    def _extract_directory(self, text: str) -> Optional[str]:
        """Extract directory path from text"""
        import re
        
        # Look for Windows paths
        win_pattern = r'["\']?([A-Za-z]:\\[^"\'<>|*?\n]+)["\']?'
        win_match = re.search(win_pattern, text)
        if win_match:
            return win_match.group(1)
        
        # Look for Unix paths or relative paths
        unix_pattern = r'["\']?(/[^"\'<>|*?\n]+|\.{1,2}/[^"\'<>|*?\n]*)["\']?'
        unix_match = re.search(unix_pattern, text)
        if unix_match:
            return unix_match.group(1)
        
        return None
