#!/usr/bin/env python3
"""
System Monitor - Complete system performance monitoring
"""

import psutil
import platform
import os
from datetime import datetime, timedelta
from pathlib import Path
from utils.logger import setup_logger

class SystemMonitor:
    def __init__(self):
        self.logger = setup_logger()
        self.system_info = self.get_static_system_info()
        print("System Monitor initialized!")
    
    def get_system_info(self):
        """Get comprehensive system information"""
        try:
            info_sections = []
            
            # System Overview
            info_sections.append(self.get_system_overview())
            
            # Performance Metrics
            info_sections.append(self.get_performance_metrics())
            
            # Storage Information
            info_sections.append(self.get_storage_info())
            
            # Network Information
            info_sections.append(self.get_network_info())
            
            return "\\n".join(info_sections)
            
        except Exception as e:
            self.logger.error(f"System info error: {e}")
            return "Error retrieving system information."
    
    def get_static_system_info(self):
        """Get static system information (cached)"""
        try:
            return {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(logical=False),
                'cpu_threads': psutil.cpu_count(logical=True),
                'total_memory': psutil.virtual_memory().total
            }
        except Exception as e:
            self.logger.error(f"Static system info error: {e}")
            return {}
    
    def get_system_overview(self):
        """Get system overview section"""
        try:
            uptime = self.get_uptime()
            
            overview = f"💻 SYSTEM OVERVIEW\\n"
            overview += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            overview += f"🖥️  OS: {self.system_info.get('system', 'Unknown')} {self.system_info.get('release', '')}\\n"
            overview += f"⚙️  Machine: {self.system_info.get('machine', 'Unknown')}\\n"
            overview += f"🔧  Processor: {self.system_info.get('processor', 'Unknown')[:50]}...\\n"
            overview += f"⏰  Uptime: {uptime}\\n"
            overview += f"🐍  Python: {self.system_info.get('python_version', 'Unknown')}\\n"
            
            return overview
            
        except Exception as e:
            self.logger.error(f"System overview error: {e}")
            return "💻 SYSTEM OVERVIEW\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\nError retrieving overview"
    
    def get_performance_metrics(self):
        """Get performance metrics section"""
        try:
            # CPU Information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            
            # Memory Information
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            memory_used_gb = memory.used / (1024**3)
            memory_available_gb = memory.available / (1024**3)
            
            # Swap Information
            swap = psutil.swap_memory()
            swap_gb = swap.total / (1024**3)
            swap_used_gb = swap.used / (1024**3)
            
            performance = f"\\n⚡ PERFORMANCE METRICS\\n"
            performance += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            performance += f"🔥  CPU Usage: {cpu_percent}%\\n"
            performance += f"📊  CPU Cores: {self.system_info.get('cpu_count', 'Unknown')} physical, {self.system_info.get('cpu_threads', 'Unknown')} logical\\n"
            
            if cpu_freq:
                performance += f"⚡  CPU Frequency: {cpu_freq.current:.0f} MHz\\n"
            
            performance += f"🧠  Memory: {memory_used_gb:.1f}GB / {memory_gb:.1f}GB ({memory.percent}% used)\\n"
            performance += f"💾  Available: {memory_available_gb:.1f}GB\\n"
            
            if swap_gb > 0:
                performance += f"🔄  Swap: {swap_used_gb:.1f}GB / {swap_gb:.1f}GB ({swap.percent}% used)\\n"
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Performance metrics error: {e}")
            return "\\n⚡ PERFORMANCE METRICS\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\nError retrieving performance data"
    
    def get_storage_info(self):
        """Get storage information section"""
        try:
            storage = f"\\n💾 STORAGE INFORMATION\\n"
            storage += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            
            # Get disk usage for all mounted drives
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = disk_usage.total / (1024**3)
                    used_gb = disk_usage.used / (1024**3)
                    free_gb = disk_usage.free / (1024**3)
                    
                    storage += f"📁  Drive {partition.device}: {used_gb:.1f}GB / {total_gb:.1f}GB\\n"
                    storage += f"    Free: {free_gb:.1f}GB ({100 - (disk_usage.used / disk_usage.total * 100):.1f}% free)\\n"
                    
                except PermissionError:
                    storage += f"📁  Drive {partition.device}: Access denied\\n"
                except Exception as e:
                    storage += f"📁  Drive {partition.device}: Error reading\\n"
            
            # Disk I/O statistics
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    read_gb = disk_io.read_bytes / (1024**3)
                    write_gb = disk_io.write_bytes / (1024**3)
                    storage += f"\\n📊  Disk I/O: Read {read_gb:.1f}GB, Write {write_gb:.1f}GB\\n"
            except:
                pass
            
            return storage
            
        except Exception as e:
            self.logger.error(f"Storage info error: {e}")
            return "\\n💾 STORAGE INFORMATION\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\nError retrieving storage information"
    
    def get_network_info(self):
        """Get network information section"""
        try:
            network = f"\\n🌐 NETWORK INFORMATION\\n"
            network += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
            
            # Network I/O statistics
            net_io = psutil.net_io_counters()
            if net_io:
                bytes_sent_mb = net_io.bytes_sent / (1024**2)
                bytes_recv_mb = net_io.bytes_recv / (1024**2)
                network += f"📡  Data Transfer: ↑{bytes_sent_mb:.1f}MB ↓{bytes_recv_mb:.1f}MB\\n"
                network += f"📊  Packets: ↑{net_io.packets_sent:,} ↓{net_io.packets_recv:,}\\n"
            
            # Network interfaces
            interfaces = psutil.net_if_addrs()
            active_interfaces = []
            
            for interface_name, addresses in interfaces.items():
                if interface_name.startswith(('Ethernet', 'Wi-Fi', 'Wireless', 'Local Area Connection')):
                    for addr in addresses:
                        if addr.family == 2:  # IPv4
                            active_interfaces.append(f"{interface_name}: {addr.address}")
            
            if active_interfaces:
                network += f"\\n🔗  Active Connections:\\n"
                for interface in active_interfaces[:3]:  # Limit to 3
                    network += f"    • {interface}\\n"
            
            return network
            
        except Exception as e:
            self.logger.error(f"Network info error: {e}")
            return "\\n🌐 NETWORK INFORMATION\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\nError retrieving network information"
    
    def get_uptime(self):
        """Get system uptime"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            uptime_delta = timedelta(seconds=uptime_seconds)
            
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except Exception as e:
            return "Unknown"
    
    def get_top_processes(self, limit=5):
        """Get top processes by CPU usage"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] is not None:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            result = f"🔄 Top {limit} Processes (by CPU usage):\\n\\n"
            
            for i, proc in enumerate(processes[:limit], 1):
                name = proc['name'][:20]  # Truncate long names
                cpu = proc['cpu_percent'] or 0
                memory = proc['memory_percent'] or 0
                
                result += f"{i}. {name:<20} CPU: {cpu:>5.1f}% RAM: {memory:>5.1f}%\\n"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Top processes error: {e}")
            return "Error retrieving top processes."
    
    def get_battery_info(self):
        """Get battery information if available"""
        try:
            battery = psutil.sensors_battery()
            
            if battery:
                percent = battery.percent
                plugged = battery.power_plugged
                
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    time_left = str(timedelta(seconds=battery.secsleft))
                    time_info = f" ({time_left} remaining)"
                else:
                    time_info = ""
                
                status = "🔌 Charging" if plugged else "🔋 On Battery"
                
                return f"\\n🔋 BATTERY STATUS\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n{status}: {percent}%{time_info}"
            else:
                return ""
                
        except Exception as e:
            return ""
    
    def get_temperature_info(self):
        """Get temperature information if available"""
        try:
            temps = psutil.sensors_temperatures()
            
            if temps:
                temp_info = f"\\n🌡️ TEMPERATURE\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n"
                
                for name, entries in temps.items():
                    for entry in entries[:2]:  # Limit entries
                        temp_info += f"{name}: {entry.current}°C\\n"
                
                return temp_info
            else:
                return ""
                
        except Exception as e:
            return ""
    
    def get_system_alerts(self):
        """Get system alerts and warnings"""
        try:
            alerts = []
            
            # CPU usage alert
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                alerts.append(f"⚠️ High CPU usage: {cpu_percent}%")
            
            # Memory usage alert
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                alerts.append(f"⚠️ High memory usage: {memory.percent}%")
            
            # Disk space alert
            for partition in psutil.disk_partitions():
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    if (disk_usage.used / disk_usage.total * 100) > 90:
                        alerts.append(f"⚠️ Low disk space on {partition.device}")
                except:
                    continue
            
            # Battery alert
            try:
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged and battery.percent < 20:
                    alerts.append(f"🔋 Low battery: {battery.percent}%")
            except:
                pass
            
            if alerts:
                return f"\\n⚠️ SYSTEM ALERTS\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n" + "\\n".join(alerts)
            else:
                return f"\\n✅ SYSTEM STATUS\\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n🟢 All systems operating normally"
                
        except Exception as e:
            self.logger.error(f"System alerts error: {e}")
            return ""
    
    def get_quick_status(self):
        """Get quick system status summary"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            status = f"Quick Status: CPU {cpu}%, RAM {memory.percent}%"
            
            # Add battery if available
            try:
                battery = psutil.sensors_battery()
                if battery:
                    status += f", Battery {battery.percent}%"
            except:
                pass
            
            return status
            
        except Exception as e:
            return "System status unavailable"
