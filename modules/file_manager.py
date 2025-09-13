#!/usr/bin/env python3
"""
File Manager - Complete file operations and organization
"""

import os
import shutil
import glob
from pathlib import Path
import json
from datetime import datetime
from utils.logger import setup_logger

class FileManager:
    def __init__(self):
        self.logger = setup_logger()
        
        # Common file extensions by category
        self.file_categories = {
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Code": [".py", ".js", ".html", ".css", ".cpp", ".java", ".php"]
        }
        
        print("File Manager initialized!")
        
    def handle_file_request(self, command):
        """Process file-related commands"""
        command = command.lower()
        
        if "find" in command or "search" in command:
            return self.find_files(command)
        elif "organize" in command or "clean" in command:
            return self.organize_downloads()
        elif "delete" in command and "empty" in command:
            return self.clean_empty_folders()
        elif "duplicate" in command:
            return self.find_duplicates()
        elif "move" in command:
            return self.move_files_by_type(command)
        else:
            return "I can help you find, organize, move files, or clean up duplicates. What would you like to do?"
    
    def find_files(self, query):
        """Find files based on query"""
        try:
            # Extract search parameters
            if ".py" in query:
                pattern = "**/*.py"
                search_type = "Python files"
            elif ".txt" in query:
                pattern = "**/*.txt"
                search_type = "text files"
            elif ".pdf" in query:
                pattern = "**/*.pdf"
                search_type = "PDF files"
            elif "image" in query or "picture" in query:
                pattern = "**/*.{jpg,jpeg,png,gif}"
                search_type = "image files"
            elif "music" in query or "song" in query:
                pattern = "**/*.{mp3,wav,flac}"
                search_type = "audio files"
            else:
                # Extract filename if mentioned
                words = query.split()
                filename = next((word for word in words if word not in 
                               ["find", "search", "for", "file", "files"]), "*")
                pattern = f"**/*{filename}*"
                search_type = f"files matching '{filename}'"
            
            # Search in common directories
            search_paths = [
                Path.home() / "Documents",
                Path.home() / "Downloads", 
                Path.home() / "Desktop",
                Path.home() / "Music",
                Path.home() / "Pictures"
            ]
            
            found_files = []
            for search_path in search_paths:
                if search_path.exists():
                    files = list(search_path.glob(pattern))
                    found_files.extend(files[:5])  # Limit results per directory
            
            if found_files:
                result = f"Found {len(found_files)} {search_type}:\\n\\n"
                for i, file in enumerate(found_files[:10], 1):
                    size = self.get_file_size(file)
                    modified = self.get_modification_date(file)
                    result += f"{i}. {file.name}\\n"
                    result += f"   Location: {file.parent}\\n"
                    result += f"   Size: {size} | Modified: {modified}\\n\\n"
                return result
            else:
                return f"No {search_type} found in common directories."
                
        except Exception as e:
            self.logger.error(f"File search error: {e}")
            return "Error occurred while searching for files."
    
    def organize_downloads(self):
        """Organize files in Downloads folder by type"""
        try:
            downloads = Path.home() / "Downloads"
            if not downloads.exists():
                return "Downloads folder not found."
            
            moved_count = 0
            created_folders = []
            
            # Create category folders and move files
            for category, extensions in self.file_categories.items():
                category_folder = downloads / category
                
                # Find files of this category
                category_files = []
                for ext in extensions:
                    category_files.extend(downloads.glob(f"*{ext}"))
                
                if category_files:
                    # Create folder if it doesn't exist
                    if not category_folder.exists():
                        category_folder.mkdir()
                        created_folders.append(category)
                    
                    # Move files
                    for file in category_files:
                        if file.is_file():
                            try:
                                destination = category_folder / file.name
                                # Handle duplicate names
                                counter = 1
                                while destination.exists():
                                    name = file.stem + f"_{counter}" + file.suffix
                                    destination = category_folder / name
                                    counter += 1
                                
                                shutil.move(str(file), str(destination))
                                moved_count += 1
                            except Exception as e:
                                self.logger.error(f"Error moving {file}: {e}")
            
            result = f"Organization complete!\\n"
            result += f"- Moved {moved_count} files\\n"
            result += f"- Created folders: {', '.join(created_folders) if created_folders else 'None'}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"File organization error: {e}")
            return "Error occurred while organizing files."
    
    def find_duplicates(self, directory=None):
        """Find duplicate files in directory"""
        try:
            if not directory:
                directory = Path.home() / "Downloads"
            
            directory = Path(directory)
            if not directory.exists():
                return f"Directory {directory} not found."
            
            # Group files by size first (faster than hash)
            size_groups = {}
            for file in directory.rglob("*"):
                if file.is_file():
                    size = file.stat().st_size
                    if size not in size_groups:
                        size_groups[size] = []
                    size_groups[size].append(file)
            
            # Find potential duplicates (same size)
            duplicates = []
            for size, files in size_groups.items():
                if len(files) > 1 and size > 0:  # Skip empty files
                    duplicates.extend(files[1:])  # Keep first, mark others as duplicates
            
            if duplicates:
                total_size = sum(f.stat().st_size for f in duplicates)
                result = f"Found {len(duplicates)} potential duplicate files:\\n"
                result += f"Total space that could be saved: {self.format_size(total_size)}\\n\\n"
                
                for i, file in enumerate(duplicates[:10], 1):
                    result += f"{i}. {file.name} ({self.get_file_size(file)})\\n"
                    result += f"   {file.parent}\\n"
                
                if len(duplicates) > 10:
                    result += f"\\n... and {len(duplicates) - 10} more files"
                    
                return result
            else:
                return "No duplicate files found."
                
        except Exception as e:
            self.logger.error(f"Duplicate search error: {e}")
            return "Error occurred while searching for duplicates."
    
    def clean_empty_folders(self, directory=None):
        """Remove empty folders"""
        try:
            if not directory:
                directory = Path.home() / "Downloads"
            
            directory = Path(directory)
            removed_count = 0
            
            # Walk through directories bottom-up
            for folder in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if folder.is_dir():
                    try:
                        # Check if folder is empty
                        if not any(folder.iterdir()):
                            folder.rmdir()
                            removed_count += 1
                    except Exception as e:
                        self.logger.error(f"Error removing {folder}: {e}")
            
            return f"Removed {removed_count} empty folders."
            
        except Exception as e:
            self.logger.error(f"Clean empty folders error: {e}")
            return "Error occurred while cleaning empty folders."
    
    def get_file_size(self, file_path):
        """Get human-readable file size"""
        try:
            size = file_path.stat().st_size
            return self.format_size(size)
        except:
            return "Unknown size"
    
    def format_size(self, size_bytes):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_modification_date(self, file_path):
        """Get file modification date"""
        try:
            timestamp = file_path.stat().st_mtime
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
        except:
            return "Unknown date"
