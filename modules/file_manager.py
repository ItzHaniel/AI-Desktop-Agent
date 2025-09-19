#!/usr/bin/env python3
"""
File Manager - Complete file operations with security and advanced features
"""

import os
import shutil
import glob
import send2trash  # pip install send2trash
from pathlib import Path
import json
from datetime import datetime
from utils.logger import setup_logger

class FileManager:
    def __init__(self):
        self.logger = setup_logger()
        
        # Password protection for file operations
        self.file_operation_password = os.getenv('FILE_OPS_PASSWORD', 'admin123')
        
        # Common file extensions by category
        self.file_categories = {
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Code": [".py", ".js", ".html", ".css", ".cpp", ".java", ".php"]
        }
        
        # Script templates for automated file creation
        self.script_templates = {
            ".py": '''#!/usr/bin/env python3
"""
{filename} - Auto-generated Python script
Created: {date}
"""

def main():
    print("Hello from {filename}!")
    # Add your code here

if __name__ == "__main__":
    main()
''',
            ".js": '''/**
 * {filename} - Auto-generated JavaScript
 * Created: {date}
 */

console.log("Hello from {filename}!");

// Add your code here
''',
            ".html": '''<!DOCTYPE html>
<!-- {filename} - Auto-generated HTML -->
<!-- Created: {date} -->
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
</head>
<body>
    <h1>Welcome to {filename}</h1>
    <p>Auto-generated on {date}</p>
</body>
</html>
''',
            ".sh": '''#!/bin/bash
# {filename} - Auto-generated Bash script
# Created: {date}

echo "Hello from {filename}!"

# Add your commands here
''',
            ".css": '''/* 
 * {filename} - Auto-generated CSS
 * Created: {date}
 */

body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}}

.container {{
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}
'''
        }
        
        print("🔒 Enhanced File Manager initialized with security features!")
        
    def authenticate(self):
        """Password authentication for file operations"""
        try:
            print("\n🔒 File operation requires authentication")
            print("💡 Tip: Set FILE_OPS_PASSWORD in your .env file")
            
            for attempt in range(3):
                user_password = input(f"🔐 Enter password (attempt {attempt + 1}/3): ").strip()
                
                if user_password == self.file_operation_password:
                    print("✅ Authentication successful!")
                    return True
                else:
                    print("❌ Incorrect password")
            
            print("🚫 Authentication failed after 3 attempts")
            return False
            
        except KeyboardInterrupt:
            print("\n🚫 Authentication cancelled")
            return False
    
    def handle_file_request(self, command):
        """Process file-related commands with extended features"""
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
            return self.move_files_interactive(command)
        elif "copy" in command:
            return self.copy_files_interactive(command)
        elif "create" in command or "new file" in command or "script" in command:
            return self.create_script_interactive()
        elif "trash" in command or "delete" in command:
            return self.delete_files_interactive(command)
        else:
            return """🗂️ File Manager Commands:
            
📂 SEARCH & DISCOVERY:
   • find python files    - Search by extension
   • find images          - Search by type  
   • search myproject     - Search by name

🗃️ ORGANIZATION:
   • organize files       - Auto-categorize downloads
   • find duplicates      - Find duplicate files
   • clean empty folders  - Remove empty directories

🔄 FILE OPERATIONS (Password Protected):
   • move files           - Move files by type
   • copy files           - Copy files by type
   • create new script    - Generate code templates
   • delete files         - Send files to trash

What would you like to do?"""
    
    def move_files_interactive(self, command):
        """Interactive file moving with authentication"""
        if not self.authenticate():
            return "❌ Authentication required for file operations"
        
        try:
            print("\n📂 INTERACTIVE FILE MOVER")
            print("=" * 30)
            
            # Get file pattern
            pattern = input("🔍 Enter file pattern (e.g., *.txt, *.py, myfile*): ").strip()
            if not pattern:
                return "❌ No file pattern provided"
            
            # Get destination
            destination = input("📁 Enter destination folder name: ").strip()
            if not destination:
                return "❌ No destination provided"
            
            # Search for files
            source_dir = Path.home() / "Downloads"  # Default search location
            destination_dir = Path.home() / destination
            
            # Create destination if it doesn't exist
            destination_dir.mkdir(parents=True, exist_ok=True)
            
            # Find matching files
            matching_files = list(source_dir.glob(pattern))
            
            if not matching_files:
                return f"❌ No files matching '{pattern}' found in {source_dir}"
            
            # Show files to be moved
            print(f"\n📋 Found {len(matching_files)} files to move:")
            for i, file in enumerate(matching_files[:10], 1):
                size = self.get_file_size(file)
                print(f"   {i}. {file.name} ({size})")
            
            if len(matching_files) > 10:
                print(f"   ... and {len(matching_files) - 10} more files")
            
            # Confirm operation
            confirm = input(f"\n✅ Move {len(matching_files)} files to {destination}? (yes/y): ").lower()
            
            if confirm in ['yes', 'y']:
                moved_count = 0
                for file in matching_files:
                    try:
                        destination_file = destination_dir / file.name
                        # Handle name conflicts
                        counter = 1
                        while destination_file.exists():
                            name = file.stem + f"_{counter}" + file.suffix
                            destination_file = destination_dir / name
                            counter += 1
                        
                        shutil.move(str(file), str(destination_file))
                        moved_count += 1
                    except Exception as e:
                        self.logger.error(f"Error moving {file}: {e}")
                
                return f"✅ Successfully moved {moved_count} files to {destination_dir}"
            else:
                return "❌ File move operation cancelled"
                
        except Exception as e:
            self.logger.error(f"Move files error: {e}")
            return f"❌ Error during file move: {str(e)}"
    
    def copy_files_interactive(self, command):
        """Interactive file copying with authentication"""
        if not self.authenticate():
            return "❌ Authentication required for file operations"
        
        try:
            print("\n📂 INTERACTIVE FILE COPIER")
            print("=" * 30)
            
            # Get source pattern
            pattern = input("🔍 Enter file pattern (e.g., *.pdf, *.jpg): ").strip()
            if not pattern:
                return "❌ No file pattern provided"
            
            # Get destination
            destination = input("📁 Enter destination folder name: ").strip()
            if not destination:
                return "❌ No destination provided"
            
            # Search for files
            source_dir = Path.home() / "Downloads"
            destination_dir = Path.home() / destination
            
            # Create destination
            destination_dir.mkdir(parents=True, exist_ok=True)
            
            # Find files
            matching_files = list(source_dir.glob(pattern))
            
            if not matching_files:
                return f"❌ No files matching '{pattern}' found"
            
            # Show preview
            total_size = sum(f.stat().st_size for f in matching_files)
            print(f"\n📋 Found {len(matching_files)} files ({self.format_size(total_size)}):")
            
            for i, file in enumerate(matching_files[:5], 1):
                size = self.get_file_size(file)
                print(f"   {i}. {file.name} ({size})")
            
            if len(matching_files) > 5:
                print(f"   ... and {len(matching_files) - 5} more files")
            
            # Confirm
            confirm = input(f"\n✅ Copy {len(matching_files)} files to {destination}? (yes/y): ").lower()
            
            if confirm in ['yes', 'y']:
                copied_count = 0
                for file in matching_files:
                    try:
                        destination_file = destination_dir / file.name
                        shutil.copy2(str(file), str(destination_file))
                        copied_count += 1
                    except Exception as e:
                        self.logger.error(f"Error copying {file}: {e}")
                
                return f"✅ Successfully copied {copied_count} files to {destination_dir}"
            else:
                return "❌ File copy operation cancelled"
                
        except Exception as e:
            self.logger.error(f"Copy files error: {e}")
            return f"❌ Error during file copy: {str(e)}"
    
    def create_script_interactive(self):
        """Interactive script creation with templates"""
        if not self.authenticate():
            return "❌ Authentication required for file creation"
        
        try:
            print("\n📝 INTERACTIVE SCRIPT GENERATOR")
            print("=" * 35)
            
            # Get filename
            filename = input("📄 Enter script filename (with extension): ").strip()
            if not filename:
                return "❌ No filename provided"
            
            # Get file extension
            file_path = Path.home() / filename
            extension = file_path.suffix.lower()
            
            # Show available templates
            if extension not in self.script_templates:
                print(f"\n💡 Available templates: {', '.join(self.script_templates.keys())}")
                extension = input("🔧 Choose template extension (.py, .js, .html, .sh, .css): ").strip()
                if extension not in self.script_templates:
                    extension = '.py'  # Default to Python
                filename = file_path.stem + extension
                file_path = Path.home() / filename
            
            # Check if file exists
            if file_path.exists():
                overwrite = input(f"⚠️ File {filename} exists. Overwrite? (yes/y): ").lower()
                if overwrite not in ['yes', 'y']:
                    return "❌ Script creation cancelled"
            
            # Generate content
            template = self.script_templates[extension]
            content = template.format(
                filename=file_path.stem,
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Make executable if shell script
            if extension == '.sh':
                os.chmod(file_path, 0o755)
            
            return f"✅ Created {extension} script: {file_path}\n📝 Template includes basic structure and comments"
            
        except Exception as e:
            self.logger.error(f"Script creation error: {e}")
            return f"❌ Error creating script: {str(e)}"
    
    def delete_files_interactive(self, command):
        """Send files to trash/recycle bin with authentication"""
        if not self.authenticate():
            return "❌ Authentication required for file deletion"
        
        try:
            print("\n🗑️ INTERACTIVE FILE DELETION")
            print("=" * 30)
            print("💡 Files will be sent to recycle bin/trash")
            
            # Get file pattern
            pattern = input("🔍 Enter file pattern to delete (e.g., *.tmp, old*): ").strip()
            if not pattern:
                return "❌ No file pattern provided"
            
            # Search location
            search_dir = Path.home() / "Downloads"
            matching_files = list(search_dir.glob(pattern))
            
            if not matching_files:
                return f"❌ No files matching '{pattern}' found"
            
            # Show files to be deleted
            total_size = sum(f.stat().st_size for f in matching_files)
            print(f"\n⚠️ Files to be deleted ({self.format_size(total_size)}):")
            
            for i, file in enumerate(matching_files[:10], 1):
                size = self.get_file_size(file)
                print(f"   {i}. {file.name} ({size})")
            
            if len(matching_files) > 10:
                print(f"   ... and {len(matching_files) - 10} more files")
            
            # Final confirmation
            confirm = input(f"\n🗑️ Send {len(matching_files)} files to trash? (yes/y): ").lower()
            
            if confirm in ['yes', 'y']:
                deleted_count = 0
                try:
                    for file in matching_files:
                        send2trash.send2trash(str(file))
                        deleted_count += 1
                    
                    return f"✅ Sent {deleted_count} files to recycle bin/trash"
                except ImportError:
                    # Fallback if send2trash not available
                    print("⚠️ send2trash not available, using permanent deletion")
                    confirm_permanent = input("⚠️ PERMANENTLY delete files? (type 'DELETE' to confirm): ")
                    
                    if confirm_permanent == 'DELETE':
                        for file in matching_files:
                            file.unlink()
                            deleted_count += 1
                        return f"⚠️ PERMANENTLY deleted {deleted_count} files"
                    else:
                        return "❌ Deletion cancelled"
            else:
                return "❌ File deletion cancelled"
                
        except Exception as e:
            self.logger.error(f"Delete files error: {e}")
            return f"❌ Error during file deletion: {str(e)}"
    
    def find_files(self, query):
        """Enhanced file finding with better natural language parsing"""
        try:
            import re
            
            # Keyword to extension mapping
            keyword_to_extension = {
                'python': '.py',
                'text': '.txt', 
                'pdf': '.pdf',
                'image': '.jpg',
                'images': '.jpg',
                'picture': '.jpg',
                'pictures': '.jpg',
                'photo': '.jpg',
                'photos': '.jpg',
                'music': '.mp3',
                'song': '.mp3',
                'songs': '.mp3',
                'audio': '.mp3',
                'video': '.mp4',
                'videos': '.mp4',
                'movie': '.mp4',
                'movies': '.mp4',
                'document': '.pdf',
                'documents': '.pdf',
                'word': '.docx',
                'excel': '.xlsx',
                'powerpoint': '.pptx',
                'zip': '.zip',
                'archive': '.zip'
            }
            
            # Clean the query
            query_lower = query.lower()
            
            # Method 1: Look for explicit extension (.py, .txt, etc.)
            extension_pattern = r'\.(\w+)'
            extension_match = re.search(extension_pattern, query)
            
            if extension_match:
                extension = '.' + extension_match.group(1).lower()
                pattern = f"**/*{extension}"
                search_type = f"files with {extension} extension"
            
            # Method 2: Look for known keywords
            elif any(keyword in query_lower for keyword in keyword_to_extension):
                for keyword, ext in keyword_to_extension.items():
                    if keyword in query_lower:
                        pattern = f"**/*{ext}"
                        search_type = f"{keyword} files ({ext})"
                        break
            
            # Method 3: Handle special cases
            elif any(word in query_lower for word in ['image', 'picture', 'photo']):
                pattern = "**/*.{jpg,jpeg,png,gif,bmp}"
                search_type = "image files"
            elif any(word in query_lower for word in ['music', 'song', 'audio']):
                pattern = "**/*.{mp3,wav,flac,aac}"
                search_type = "audio files"
            elif any(word in query_lower for word in ['video', 'movie']):
                pattern = "**/*.{mp4,avi,mkv,mov}"
                search_type = "video files"
            elif any(word in query_lower for word in ['document', 'doc']):
                pattern = "**/*.{pdf,doc,docx,txt}"
                search_type = "document files"
            
            # Method 4: Extract actual filename (improved logic)
            else:
                # Remove common command words and extract meaningful terms
                stop_words = ['could', 'you', 'help', 'me', 'to', 'find', 'search', 'for', 'file', 'files', 'by', 'extension', 'with', 'named', 'called']
                words = [word for word in query_lower.split() if word not in stop_words and len(word) > 2]
                
                if words:
                    # Use the longest/most meaningful word
                    filename = max(words, key=len)
                    pattern = f"**/*{filename}*"
                    search_type = f"files matching '{filename}'"
                else:
                    # No clear criteria - ask for clarification
                    return """🔍 File Search Help:

    I need more specific search criteria. Try:

    📁 **By Extension:**
    • "find .py files"
    • "search .txt files" 
    • "find .pdf documents"

    📂 **By Type:**
    • "find python files"
    • "search images"
    • "find music files"
    • "search documents"

    📄 **By Name:**
    • "find project files"
    • "search report"
    • "find mydata"

    Examples:
    • "find all python files"
    • "search for .jpg images"  
    • "find files named report"
    """
            
            # Search in common directories
            search_paths = [
                Path.home() / "Documents",
                Path.home() / "Downloads", 
                Path.home() / "Desktop",
                Path.home() / "Music",
                Path.home() / "Pictures",
                Path.home() / "Videos"
            ]
            
            found_files = []
            for search_path in search_paths:
                if search_path.exists():
                    try:
                        if '{' in pattern:  # Multiple extensions
                            # Handle multiple extensions pattern
                            base_pattern = pattern.split('.{')[0] + '.'
                            extensions = pattern.split('{')[1].split('}')[0].split(',')
                            for ext in extensions:
                                files = list(search_path.glob(f"{base_pattern}{ext}"))
                                found_files.extend(files[:5])  # Limit per extension
                        else:
                            files = list(search_path.glob(pattern))
                            found_files.extend(files[:5])  # Limit results per directory
                    except Exception as e:
                        self.logger.error(f"Error searching in {search_path}: {e}")
                        continue
            
            # Remove duplicates and limit total results
            found_files = list(dict.fromkeys(found_files))[:20]  # Remove duplicates, limit to 20
            
            if found_files:
                result = f"🔍 Found {len(found_files)} {search_type}:\n\n"
                for i, file in enumerate(found_files[:15], 1):  # Show max 15
                    size = self.get_file_size(file)
                    modified = self.get_modification_date(file)
                    result += f"{i}. 📄 {file.name}\n"
                    result += f"   📂 Location: {file.parent}\n"
                    result += f"   📊 Size: {size} | 📅 Modified: {modified}\n\n"
                
                if len(found_files) > 15:
                    result += f"... and {len(found_files) - 15} more files\n"
                
                return result
            else:
                return f"❌ No {search_type} found in common directories.\n\n💡 Try:\n• Different file extension\n• More specific filename\n• 'organize files' to clean up first"
                
        except Exception as e:
            self.logger.error(f"Enhanced file search error: {e}")
            return "❌ Error occurred while searching for files. Try being more specific with your search criteria."

    
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
