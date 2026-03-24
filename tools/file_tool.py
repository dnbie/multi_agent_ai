"""
File Tool - File Operations Module
Handles reading, writing, organizing, and managing files
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class FileTool:
    """
    File operations tool for reading, writing, and managing files.
    """
    
    # Common file type categories
    FILE_CATEGORIES = {
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
        "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
        "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml", ".yaml", ".yml"],
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
        "video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
        "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "data": [".csv", ".json", ".xml", ".sql", ".db", ".sqlite"]
    }
    
    def __init__(self, base_dir: str = None):
        """
        Initialize file tool.
        
        Args:
            base_dir: Base directory for operations
        """
        from config import BASE_DIR
        self.base_dir = Path(base_dir) if base_dir else BASE_DIR
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, any]:
        """
        Read content from a file.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
            
        Returns:
            Dictionary with content and metadata
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Not a file: {file_path}"
            }
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            stat = path.stat()
            
            return {
                "success": True,
                "content": content,
                "file_name": path.name,
                "file_path": str(path.absolute()),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": path.suffix,
                "lines": len(content.split('\n'))
            }
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": f"Cannot read file with {encoding} encoding. Try a different encoding."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}"
            }
    
    def write_file(
        self,
        file_path: str,
        content: str,
        encoding: str = 'utf-8',
        overwrite: bool = False
    ) -> Dict[str, any]:
        """
        Write content to a file.
        
        Args:
            file_path: Path to save the file
            content: Content to write
            encoding: File encoding
            overwrite: Whether to overwrite existing file
            
        Returns:
            Result dictionary
        """
        path = Path(file_path)
        
        if path.exists() and not overwrite:
            return {
                "success": False,
                "error": f"File already exists: {file_path}. Set overwrite=True to replace."
            }
        
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"File saved successfully: {file_path}",
                "file_path": str(path.absolute()),
                "size": len(content.encode(encoding))
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error writing file: {str(e)}"
            }
    
    def append_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> Dict[str, any]:
        """Append content to a file"""
        path = Path(file_path)
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'a', encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"Content appended to: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error appending to file: {str(e)}"
            }
    
    def copy_file(self, source: str, destination: str) -> Dict[str, any]:
        """Copy a file"""
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            return {"success": False, "error": f"Source not found: {source}"}
        
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            
            return {
                "success": True,
                "message": f"Copied {source} to {destination}",
                "source": source,
                "destination": str(dst.absolute())
            }
        except Exception as e:
            return {"success": False, "error": f"Copy failed: {str(e)}"}
    
    def move_file(self, source: str, destination: str) -> Dict[str, any]:
        """Move a file"""
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            return {"success": False, "error": f"Source not found: {source}"}
        
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            
            return {
                "success": True,
                "message": f"Moved {source} to {destination}",
                "source": source,
                "destination": str(dst.absolute())
            }
        except Exception as e:
            return {"success": False, "error": f"Move failed: {str(e)}"}
    
    def rename_file(self, file_path: str, new_name: str) -> Dict[str, any]:
        """Rename a file"""
        path = Path(file_path)
        
        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}
        
        new_path = path.parent / new_name
        
        try:
            path.rename(new_path)
            
            return {
                "success": True,
                "message": f"Renamed to: {new_name}",
                "old_path": file_path,
                "new_path": str(new_path.absolute())
            }
        except Exception as e:
            return {"success": False, "error": f"Rename failed: {str(e)}"}
    
    def delete_file(self, file_path: str) -> Dict[str, any]:
        """Delete a file"""
        path = Path(file_path)
        
        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}
        
        try:
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
            
            return {
                "success": True,
                "message": f"Deleted: {file_path}"
            }
        except Exception as e:
            return {"success": False, "error": f"Delete failed: {str(e)}"}
    
    def list_directory(
        self,
        directory: str,
        recursive: bool = False,
        pattern: str = None
    ) -> Dict[str, any]:
        """
        List contents of a directory.
        
        Args:
            directory: Directory path
            recursive: Whether to list recursively
            pattern: Glob pattern to filter files
            
        Returns:
            Dictionary with file list
        """
        path = Path(directory)
        
        if not path.exists():
            return {"success": False, "error": f"Directory not found: {directory}"}
        
        if not path.is_dir():
            return {"success": False, "error": f"Not a directory: {directory}"}
        
        try:
            if pattern:
                if recursive:
                    files = list(path.rglob(pattern))
                else:
                    files = list(path.glob(pattern))
            else:
                if recursive:
                    files = list(path.rglob("*"))
                else:
                    files = list(path.iterdir())
            
            items = []
            for f in files:
                items.append({
                    "name": f.name,
                    "path": str(f.absolute()),
                    "is_file": f.is_file(),
                    "is_dir": f.is_dir(),
                    "size": f.stat().st_size if f.is_file() else None,
                    "extension": f.suffix if f.is_file() else None
                })
            
            return {
                "success": True,
                "directory": directory,
                "count": len(items),
                "items": items
            }
        except Exception as e:
            return {"success": False, "error": f"Error listing directory: {str(e)}"}
    
    def get_file_category(self, file_path: str) -> str:
        """Get category of a file based on extension"""
        ext = Path(file_path).suffix.lower()
        
        for category, extensions in self.FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        
        return "other"
    
    def organize_by_type(
        self,
        source_dir: str,
        dest_dir: str = None,
        move_files: bool = False
    ) -> Dict[str, any]:
        """
        Organize files by type into categorized folders.
        
        Args:
            source_dir: Source directory
            dest_dir: Destination directory (defaults to source_dir/organized)
            move_files: Whether to move files (vs copy)
            
        Returns:
            Organization result
        """
        source = Path(source_dir)
        dest = Path(dest_dir) if dest_dir else source / "organized"
        
        if not source.exists():
            return {"success": False, "error": f"Directory not found: {source_dir}"}
        
        results = {"organized": [], "errors": []}
        
        try:
            for file_path in source.iterdir():
                if file_path.is_file():
                    category = self.get_file_category(str(file_path))
                    category_dir = dest / category
                    category_dir.mkdir(parents=True, exist_ok=True)
                    
                    dest_file = category_dir / file_path.name
                    
                    try:
                        if move_files:
                            shutil.move(str(file_path), str(dest_file))
                            action = "moved"
                        else:
                            shutil.copy2(file_path, dest_file)
                            action = "copied"
                        
                        results["organized"].append({
                            "file": file_path.name,
                            "category": category,
                            "action": action,
                            "destination": str(dest_file)
                        })
                    except Exception as e:
                        results["errors"].append({
                            "file": file_path.name,
                            "error": str(e)
                        })
            
            return {
                "success": True,
                "message": f"Organized {len(results['organized'])} files",
                "results": results,
                "destination": str(dest)
            }
        except Exception as e:
            return {"success": False, "error": f"Organization failed: {str(e)}"}
    
    def batch_rename(
        self,
        directory: str,
        pattern: str,
        replacement: str,
        preview: bool = True
    ) -> Dict[str, any]:
        """
        Batch rename files in a directory.
        
        Args:
            directory: Directory containing files
            pattern: Pattern to find in filenames
            replacement: Replacement string
            preview: Whether to preview changes without applying
            
        Returns:
            Rename results
        """
        import re
        
        path = Path(directory)
        
        if not path.exists() or not path.is_dir():
            return {"success": False, "error": f"Invalid directory: {directory}"}
        
        changes = []
        
        for file_path in path.iterdir():
            if file_path.is_file():
                old_name = file_path.name
                new_name = re.sub(pattern, replacement, old_name)
                
                if old_name != new_name:
                    changes.append({
                        "old_name": old_name,
                        "new_name": new_name,
                        "old_path": str(file_path),
                        "new_path": str(file_path.parent / new_name)
                    })
        
        if preview:
            return {
                "success": True,
                "preview": True,
                "changes": changes,
                "message": f"Preview: {len(changes)} files would be renamed"
            }
        
        # Apply changes
        applied = []
        errors = []
        
        for change in changes:
            try:
                Path(change["old_path"]).rename(change["new_path"])
                applied.append(change)
            except Exception as e:
                errors.append({"file": change["old_name"], "error": str(e)})
        
        return {
            "success": True,
            "preview": False,
            "applied": applied,
            "errors": errors,
            "message": f"Renamed {len(applied)} files"
        }
    
    def get_file_info(self, file_path: str) -> Dict[str, any]:
        """Get detailed information about a file"""
        path = Path(file_path)
        
        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}
        
        stat = path.stat()
        
        return {
            "success": True,
            "name": path.name,
            "path": str(path.absolute()),
            "extension": path.suffix,
            "size": stat.st_size,
            "size_formatted": self._format_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "category": self.get_file_category(file_path)
        }
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def search_files(
        self,
        directory: str,
        query: str,
        search_content: bool = False
    ) -> Dict[str, any]:
        """
        Search for files by name or content.
        
        Args:
            directory: Directory to search
            query: Search query
            search_content: Whether to search file contents
            
        Returns:
            Search results
        """
        path = Path(directory)
        
        if not path.exists():
            return {"success": False, "error": f"Directory not found: {directory}"}
        
        results = []
        query_lower = query.lower()
        
        for file_path in path.rglob("*"):
            if file_path.is_file():
                # Search by name
                if query_lower in file_path.name.lower():
                    results.append({
                        "file": file_path.name,
                        "path": str(file_path),
                        "match_type": "filename"
                    })
                # Search content
                elif search_content:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if query_lower in content.lower():
                                results.append({
                                    "file": file_path.name,
                                    "path": str(file_path),
                                    "match_type": "content"
                                })
                    except:
                        pass
        
        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        }
