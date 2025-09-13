#!/usr/bin/env python3
"""
Application Launcher - Complete Windows application launching system
"""

import subprocess
import os
import winreg
from pathlib import Path
import psutil
from utils.logger import setup_logger

class AppLauncher:
    def __init__(self):
        self.logger = setup_logger()
        
        # Common applications mapping
        self.common_apps = {
            # System apps
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "file explorer": "explorer.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "registry editor": "regedit.exe",
            "system information": "msinfo32.exe",
            
            # Browsers
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "internet explorer": "iexplore.exe",
            
            # Office apps
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "outlook": "outlook.exe",
            
            # Media
            "windows media player": "wmplayer.exe",
            "media player": "wmplayer.exe",
            
            # Development
            "visual studio code": "code.exe",
            "vscode": "code.exe",
            "code": "code.exe",
            "notepad++": "notepad++.exe"
        }
        
        # Cache for installed applications
        self.installed_apps = {}
        self.scan_installed_apps()
        
        print("Application Launcher initialized!")
    
    def launch_application(self, command):
        """Main application launching function"""
        try:
            app_name = self.extract_app_name(command)
            
            if not app_name:
                return "Please specify which application to launch."
            
            # Try common apps first
            if app_name in self.common_apps:
                return self.launch_system_app(app_name)
            
            # Try installed applications
            app_path = self.find_installed_app(app_name)
            if app_path:
                return self.launch_custom_app(app_path, app_name)
            
            # Try web search as fallback
            if any(word in app_name for word in ["website", "site", "web"]):
                return self.open_website(command)
            
            # Suggest alternatives
            suggestions = self.suggest_similar_apps(app_name)
            if suggestions:
                return f"Could not find '{app_name}'. Did you mean: {', '.join(suggestions)}?"
            
            return f"Could not find application '{app_name}'. Try using the full application name."
            
        except Exception as e:
            self.logger.error(f"App launch error: {e}")
            return f"Error launching application: {str(e)}"
    
    def extract_app_name(self, command):
        """Extract application name from voice command"""
        words_to_remove = ["open", "launch", "start", "run", "execute", "the", "a", "an"]
        words = command.lower().split()
        app_words = [word for word in words if word not in words_to_remove]
        return " ".join(app_words)
    
    def launch_system_app(self, app_name):
        """Launch system/common applications"""
        try:
            app_executable = self.common_apps[app_name]
            
            # Special handling for certain apps
            if app_name == "file explorer":
                subprocess.Popen(["explorer.exe"])
            elif app_name == "control panel":
                subprocess.Popen(["control.exe"])
            else:
                subprocess.Popen(app_executable, shell=True)
            
            return f"Launching {app_name.title()}"
            
        except Exception as e:
            self.logger.error(f"System app launch error: {e}")
            return f"Error launching {app_name}"
    
    def find_installed_app(self, app_name):
        """Find installed application path"""
        app_name_lower = app_name.lower()
        
        # Check cached installed apps
        for installed_name, path in self.installed_apps.items():
            if app_name_lower in installed_name.lower():
                return path
        
        # Search in common installation directories
        search_paths = [
            "C:/Program Files",
            "C:/Program Files (x86)",
            str(Path.home() / "AppData/Local"),
            str(Path.home() / "AppData/Roaming"),
            "C:/Users/Public/Desktop"
        ]
        
        for search_path in search_paths:
            found_path = self.search_directory_for_app(search_path, app_name)
            if found_path:
                return found_path
        
        return None
    
    def search_directory_for_app(self, directory, app_name):
        """Search directory for application executable"""
        try:
            if not os.path.exists(directory):
                return None
            
            # Limit search depth for performance
            for root, dirs, files in os.walk(directory):
                # Skip deep nested directories
                depth = root[len(directory):].count(os.sep)
                if depth > 3:
                    continue
                
                for file in files:
                    if file.lower().endswith('.exe'):
                        if app_name.lower() in file.lower():
                            return os.path.join(root, file)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Directory search error: {e}")
            return None
    
    def launch_custom_app(self, app_path, app_name):
        """Launch custom/installed application"""
        try:
            subprocess.Popen(app_path, shell=True)
            return f"Launching {app_name.title()}"
            
        except Exception as e:
            self.logger.error(f"Custom app launch error: {e}")
            return f"Error launching {app_name}"
    
    def scan_installed_apps(self):
        """Scan for installed applications in registry and common locations"""
        try:
            # Scan Windows Registry for installed programs
            self.scan_registry_apps()
            
            # Scan desktop shortcuts
            self.scan_desktop_shortcuts()
            
            print(f"Found {len(self.installed_apps)} installed applications")
            
        except Exception as e:
            self.logger.error(f"App scanning error: {e}")
    
    def scan_registry_apps(self):
        """Scan Windows Registry for installed applications"""
        try:
            # Registry keys to check
            registry_keys = [
                (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
                (winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall")
            ]
            
            for hkey, subkey_path in registry_keys:
                try:
                    with winreg.OpenKey(hkey, subkey_path) as key:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                        
                                        if install_location and os.path.exists(install_location):
                                            self.installed_apps[display_name] = install_location
                                    except FileNotFoundError:
                                        pass
                                i += 1
                            except OSError:
                                break
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Registry scan error: {e}")
    
    def scan_desktop_shortcuts(self):
        """Scan desktop shortcuts for applications"""
        try:
            desktop_paths = [
                Path.home() / "Desktop",
                Path("C:/Users/Public/Desktop")
            ]
            
            for desktop_path in desktop_paths:
                if desktop_path.exists():
                    for shortcut in desktop_path.glob("*.lnk"):
                        # Simple shortcut name mapping
                        app_name = shortcut.stem
                        self.installed_apps[app_name] = str(shortcut)
                        
        except Exception as e:
            self.logger.error(f"Desktop scan error: {e}")
    
    def suggest_similar_apps(self, app_name):
        """Suggest similar application names"""
        suggestions = []
        app_name_lower = app_name.lower()
        
        # Check common apps
        for common_app in self.common_apps.keys():
            if any(word in common_app for word in app_name_lower.split()):
                suggestions.append(common_app)
        
        # Check installed apps
        for installed_app in list(self.installed_apps.keys())[:5]:  # Limit suggestions
            if any(word in installed_app.lower() for word in app_name_lower.split()):
                suggestions.append(installed_app.split()[0])  # First word only
        
        return suggestions[:3]  # Max 3 suggestions
    
    def open_website(self, command):
        """Open website in default browser"""
        try:
            # Extract URL or search term
            if "http" in command:
                # Direct URL
                url = command.split("http")[1]
                url = "http" + url.split()[0]
            else:
                # Search term
                search_term = command.replace("open", "").replace("website", "").strip()
                url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
            
            subprocess.Popen(f'start {url}', shell=True)
            return f"Opening website in browser"
            
        except Exception as e:
            self.logger.error(f"Website open error: {e}")
            return "Error opening website"
    
    def list_running_apps(self):
        """List currently running applications"""
        try:
            running_apps = []
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['exe'] and proc.info['name'].endswith('.exe'):
                        app_name = proc.info['name'][:-4]  # Remove .exe
                        if app_name not in running_apps and len(app_name) > 2:
                            running_apps.append(app_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if running_apps:
                result = f"Currently running applications ({len(running_apps)}):\\n\\n"
                for i, app in enumerate(sorted(running_apps)[:15], 1):  # Limit to 15
                    result += f"{i}. {app}\\n"
                
                if len(running_apps) > 15:
                    result += f"\\n... and {len(running_apps) - 15} more applications"
                
                return result
            else:
                return "No applications currently running."
                
        except Exception as e:
            self.logger.error(f"List running apps error: {e}")
            return "Error getting running applications list."
    
    def close_application(self, app_name):
        """Close running application"""
        try:
            app_name = app_name.lower()
            closed_count = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name in proc.info['name'].lower():
                        proc.terminate()
                        closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if closed_count > 0:
                return f"Closed {closed_count} instance(s) of {app_name}"
            else:
                return f"No running instances of {app_name} found"
                
        except Exception as e:
            self.logger.error(f"Close app error: {e}")
            return f"Error closing {app_name}"
