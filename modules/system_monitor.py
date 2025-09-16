#!/usr/bin/env python3
"""
Enhanced System Monitor - Clean, comprehensive system monitoring for desktop AI agent
"""

import psutil
import platform
import os
import json
import openai
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
import time
import threading
from utils.logger import setup_logger


class SystemMonitor:
    def __init__(self):
        self.logger = setup_logger()
        
        # Historical data storage (last 60 readings)
        self.cpu_history = deque(maxlen=60)
        self.memory_history = deque(maxlen=60)
        self.network_history = deque(maxlen=60)
        
        # System baseline info
        self.system_info = self.get_static_system_info()
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Groq integration for intelligent system analysis
        self.setup_groq()
        
        # Performance thresholds
        self.thresholds = {
            'cpu_warning': 75,
            'cpu_critical': 90,
            'memory_warning': 80,
            'memory_critical': 95,
            'disk_warning': 85,
            'disk_critical': 95,
            'battery_low': 20,
            'battery_critical': 10
        }
        
        print("Enhanced System Monitor initialized")
    
    def setup_groq(self):
        """Setup Groq AI for system analysis"""
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if groq_api_key:
            try:
                self.groq_client = openai.OpenAI(
                    api_key=groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                self.groq_model = "llama-3.1-8b-instant"
                print("AI system analysis enabled")
            except Exception as e:
                self.logger.error(f"Groq setup error: {e}")
                self.groq_client = None
        else:
            self.groq_client = None
    
    def classify_intent(self, command):
        """Use AI to classify whether this is a system monitor request or conversation"""
        system_monitor_keywords = [
            'cpu usage', 'memory usage', 'disk space', 'system performance', 
            'running processes', 'computer stats', 'battery status', 'temperature',
            'network status', 'top processes', 'system alerts', 'uptime',
            'storage status', 'performance check', 'system health', 'system info',
            'disk usage', 'ram usage', 'cpu load', 'system overview', 'monitor',
            'sensors', 'thermal', 'cooling', 'fan speed', 'power consumption',
            'load average', 'swap usage', 'virtual memory', 'physical memory'
        ]
        
        if any(keyword in command.lower() for keyword in system_monitor_keywords):
            return 'system_monitor'
        
        # For ambiguous cases, use Groq to classify intent
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Classify if this request is about 'system_monitor' (computer performance, hardware stats, system resources) or 'conversation' (general chat, questions, other topics). Reply with only one word."},
                        {"role": "user", "content": command}
                    ],
                    model=self.groq_model,
                    max_tokens=10,
                    temperature=0.1
                )
                classification = response.choices[0].message.content.strip().lower()
                return classification if classification in ['system_monitor', 'conversation'] else 'conversation'
            except Exception as e:
                self.logger.error(f"AI intent classification error: {e}")
        
        return 'conversation'
    
    def get_static_system_info(self):
        """Get and cache static system information"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            
            return {
                'hostname': platform.node(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor().split()[0] if platform.processor() else "Unknown",
                'architecture': platform.architecture()[0],
                'python_version': platform.python_version(),
                'cpu_count_physical': psutil.cpu_count(logical=False),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 1),
                'boot_time': boot_time,
                'timezone': datetime.now().astimezone().tzname()
            }
        except Exception as e:
            self.logger.error(f"Static system info error: {e}")
            return {}
    
    def start_monitoring(self):
        """Start continuous monitoring in background"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            return "System monitoring started"
        return "Monitoring already active"
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
        return "System monitoring stopped"
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                network = psutil.net_io_counters()
                
                # Store in history
                timestamp = datetime.now()
                self.cpu_history.append({'time': timestamp, 'value': cpu_percent})
                self.memory_history.append({'time': timestamp, 'value': memory.percent})
                
                if network:
                    self.network_history.append({
                        'time': timestamp, 
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv
                    })
                
                time.sleep(5)  # Collect every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)
    
    def get_system_info(self):
        """Get system information - maintains compatibility with existing code"""
        return self.get_system_overview()
    
    def get_system_overview(self):
        """Get clean, readable system overview"""
        try:
            uptime = self.get_uptime()
            info = self.system_info
            
            overview = f"""SYSTEM OVERVIEW
{'-' * 50}
Computer: {info.get('hostname', 'Unknown')}
OS: {info.get('system', 'Unknown')} {info.get('release', '')}
Architecture: {info.get('architecture', 'Unknown')}
Processor: {info.get('processor', 'Unknown')}
CPU Cores: {info.get('cpu_count_physical', 0)} physical, {info.get('cpu_count_logical', 0)} logical
Memory: {info.get('total_memory_gb', 0)} GB
Uptime: {uptime}
Boot Time: {info.get('boot_time', 'Unknown').strftime('%Y-%m-%d %H:%M:%S') if info.get('boot_time') else 'Unknown'}
Python: {info.get('python_version', 'Unknown')}"""
            
            return overview
            
        except Exception as e:
            self.logger.error(f"System overview error: {e}")
            return "Error retrieving system overview"
    
    def get_performance_status(self, detailed=False):
        """Get current performance metrics"""
        try:
            # Get current metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # CPU frequency if available
            try:
                cpu_freq = psutil.cpu_freq()
                freq_info = f" @ {cpu_freq.current:.0f} MHz" if cpu_freq else ""
            except:
                freq_info = ""
            
            # Basic status
            status = f"""PERFORMANCE STATUS
{'-' * 50}
CPU Usage: {cpu_percent:.1f}%{freq_info} {self._get_status_indicator('cpu', cpu_percent)}
Memory: {memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB ({memory.percent:.1f}%) {self._get_status_indicator('memory', memory.percent)}
Available: {memory.available / (1024**3):.1f} GB
Disk Usage: {disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB ({disk.used / disk.total * 100:.1f}%) {self._get_status_indicator('disk', disk.used / disk.total * 100)}"""
            
            # Add swap if available
            swap = psutil.swap_memory()
            if swap.total > 0:
                status += f"\nSwap: {swap.used / (1024**3):.1f} GB / {swap.total / (1024**3):.1f} GB ({swap.percent:.1f}%)"
            
            # Add detailed info if requested
            if detailed:
                status += f"\n\n{self._get_detailed_performance()}"
            
            return status
            
        except Exception as e:
            self.logger.error(f"Performance status error: {e}")
            return "Error retrieving performance status"
    
    def _get_status_indicator(self, metric_type, value):
        """Get status indicator based on thresholds"""
        if metric_type == 'cpu':
            if value >= self.thresholds['cpu_critical']:
                return "[CRITICAL]"
            elif value >= self.thresholds['cpu_warning']:
                return "[WARNING]"
            else:
                return "[OK]"
        elif metric_type == 'memory':
            if value >= self.thresholds['memory_critical']:
                return "[CRITICAL]"
            elif value >= self.thresholds['memory_warning']:
                return "[WARNING]"
            else:
                return "[OK]"
        elif metric_type == 'disk':
            if value >= self.thresholds['disk_critical']:
                return "[CRITICAL]"
            elif value >= self.thresholds['disk_warning']:
                return "[WARNING]"
            else:
                return "[OK]"
        return ""
    
    def _get_detailed_performance(self):
        """Get detailed performance information"""
        try:
            details = []
            
            # Load averages (Unix-like systems)
            try:
                load_avg = os.getloadavg()
                details.append(f"Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
            except:
                pass
            
            # Process count
            process_count = len(psutil.pids())
            details.append(f"Running Processes: {process_count}")
            
            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io:
                details.append(f"Network I/O: {net_io.bytes_sent / (1024**2):.1f} MB sent, {net_io.bytes_recv / (1024**2):.1f} MB received")
            
            # Disk I/O
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    details.append(f"Disk I/O: {disk_io.read_bytes / (1024**2):.1f} MB read, {disk_io.write_bytes / (1024**2):.1f} MB written")
            except:
                pass
            
            return "\n".join(details) if details else ""
            
        except Exception as e:
            return ""
    
    def get_storage_status(self):
        """Get storage information for all drives"""
        try:
            storage_info = "STORAGE STATUS\n" + "-" * 50
            
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = disk_usage.total / (1024**3)
                    used_gb = disk_usage.used / (1024**3)
                    free_gb = disk_usage.free / (1024**3)
                    used_percent = (disk_usage.used / disk_usage.total) * 100
                    
                    # Clean device name
                    device = partition.device.replace('\\', '') if partition.device else partition.mountpoint
                    
                    storage_info += f"\n{device}: {used_gb:.1f} GB / {total_gb:.1f} GB ({used_percent:.1f}%) {self._get_status_indicator('disk', used_percent)}"
                    storage_info += f"\n  Free: {free_gb:.1f} GB, Type: {partition.fstype or 'Unknown'}"
                    
                except (PermissionError, FileNotFoundError):
                    storage_info += f"\n{partition.device}: Access denied"
                except Exception as e:
                    storage_info += f"\n{partition.device}: Error reading ({str(e)[:30]})"
            
            return storage_info
            
        except Exception as e:
            self.logger.error(f"Storage status error: {e}")
            return "Error retrieving storage information"
    
    def get_network_status(self):
        """Get network interface and traffic information"""
        try:
            network_info = "NETWORK STATUS\n" + "-" * 50
            
            # Network I/O counters
            net_io = psutil.net_io_counters()
            if net_io:
                sent_gb = net_io.bytes_sent / (1024**3)
                recv_gb = net_io.bytes_recv / (1024**3)
                network_info += f"\nTotal Traffic: {sent_gb:.2f} GB sent, {recv_gb:.2f} GB received"
                network_info += f"\nPackets: {net_io.packets_sent:,} sent, {net_io.packets_recv:,} received"
            
            # Active network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            network_info += "\n\nActive Interfaces:"
            
            for interface_name, addresses in interfaces.items():
                # Skip loopback and irrelevant interfaces
                if interface_name.lower() in ['lo', 'loopback']:
                    continue
                
                # Get interface status
                if interface_name in stats:
                    stat = stats[interface_name]
                    if not stat.isup:
                        continue
                
                network_info += f"\n  {interface_name}:"
                
                for addr in addresses:
                    if addr.family == 2:  # IPv4
                        network_info += f"\n    IPv4: {addr.address}"
                    elif addr.family == 23:  # IPv6 (on some systems)
                        network_info += f"\n    IPv6: {addr.address[:20]}..."
                
                # Add speed if available
                if interface_name in stats:
                    speed = stats[interface_name].speed
                    if speed and speed > 0:
                        network_info += f"\n    Speed: {speed} Mbps"
            
            return network_info
            
        except Exception as e:
            self.logger.error(f"Network status error: {e}")
            return "Error retrieving network information"
    
    def get_top_processes(self, limit=10, sort_by='cpu'):
        """Get top processes by CPU or memory usage"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] is not None:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes
            if sort_by == 'memory':
                processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
                header = f"TOP {limit} PROCESSES (by Memory Usage)"
            else:
                processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
                header = f"TOP {limit} PROCESSES (by CPU Usage)"
            
            result = f"{header}\n{'-' * 50}\n"
            result += f"{'PID':<8} {'Name':<20} {'CPU%':<8} {'MEM%':<8} {'User':<15}\n"
            result += "-" * 65 + "\n"
            
            for proc in processes[:limit]:
                pid = proc['pid']
                name = (proc['name'] or 'Unknown')[:19]
                cpu = proc['cpu_percent'] or 0
                memory = proc['memory_percent'] or 0
                user = (proc['username'] or 'Unknown')[:14]
                
                result += f"{pid:<8} {name:<20} {cpu:>6.1f}% {memory:>6.1f}% {user:<15}\n"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Top processes error: {e}")
            return "Error retrieving process information"
    
    def get_system_alerts(self):
        """Get system alerts and recommendations"""
        try:
            alerts = []
            recommendations = []
            
            # Performance alerts
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent >= self.thresholds['cpu_critical']:
                alerts.append(f"CRITICAL: CPU usage at {cpu_percent:.1f}%")
                recommendations.append("Consider closing unnecessary applications")
            elif cpu_percent >= self.thresholds['cpu_warning']:
                alerts.append(f"WARNING: High CPU usage at {cpu_percent:.1f}%")
            
            # Memory alerts
            memory = psutil.virtual_memory()
            if memory.percent >= self.thresholds['memory_critical']:
                alerts.append(f"CRITICAL: Memory usage at {memory.percent:.1f}%")
                recommendations.append("Close memory-intensive applications")
            elif memory.percent >= self.thresholds['memory_warning']:
                alerts.append(f"WARNING: High memory usage at {memory.percent:.1f}%")
            
            # Disk space alerts
            try:
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                if disk_percent >= self.thresholds['disk_critical']:
                    alerts.append(f"CRITICAL: Low disk space ({disk_percent:.1f}% used)")
                    recommendations.append("Delete unnecessary files or move data to external storage")
                elif disk_percent >= self.thresholds['disk_warning']:
                    alerts.append(f"WARNING: Disk space low ({disk_percent:.1f}% used)")
            except:
                pass
            
            # Battery alerts (if applicable)
            try:
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged:
                    if battery.percent <= self.thresholds['battery_critical']:
                        alerts.append(f"CRITICAL: Battery at {battery.percent}%")
                        recommendations.append("Connect power adapter immediately")
                    elif battery.percent <= self.thresholds['battery_low']:
                        alerts.append(f"WARNING: Low battery at {battery.percent}%")
            except:
                pass
            
            # Compile response
            if alerts or recommendations:
                result = "SYSTEM ALERTS\n" + "-" * 50
                
                if alerts:
                    result += "\nAlerts:"
                    for alert in alerts:
                        result += f"\n  • {alert}"
                
                if recommendations:
                    result += "\n\nRecommendations:"
                    for rec in recommendations:
                        result += f"\n  • {rec}"
                
                return result
            else:
                return "SYSTEM STATUS\n" + "-" * 50 + "\nAll systems operating normally"
                
        except Exception as e:
            self.logger.error(f"System alerts error: {e}")
            return "Error checking system alerts"
    
    def get_battery_status(self):
        """Get detailed battery information"""
        try:
            battery = psutil.sensors_battery()
            
            if not battery:
                return "No battery detected (desktop system)"
            
            status = "BATTERY STATUS\n" + "-" * 50
            status += f"\nCharge Level: {battery.percent}%"
            status += f"\nPower Source: {'AC Power' if battery.power_plugged else 'Battery'}"
            
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft > 0:
                time_left = timedelta(seconds=battery.secsleft)
                hours, remainder = divmod(time_left.total_seconds(), 3600)
                minutes = remainder // 60
                
                if battery.power_plugged:
                    status += f"\nTime to Full Charge: {int(hours)}h {int(minutes)}m"
                else:
                    status += f"\nTime Remaining: {int(hours)}h {int(minutes)}m"
            
            # Battery health indicator
            if battery.percent <= self.thresholds['battery_critical']:
                status += "\nStatus: CRITICAL - Connect charger immediately"
            elif battery.percent <= self.thresholds['battery_low']:
                status += "\nStatus: LOW - Consider charging soon"
            else:
                status += "\nStatus: Good"
            
            return status
            
        except Exception as e:
            return "Error retrieving battery information"
    
    def get_temperature_status(self):
        """Get system temperature information"""
        try:
            temps = psutil.sensors_temperatures()
            
            if not temps:
                return "Temperature sensors not available"
            
            temp_info = "TEMPERATURE STATUS\n" + "-" * 50
            
            for name, entries in temps.items():
                temp_info += f"\n{name}:"
                for entry in entries[:3]:  # Limit to 3 entries per sensor
                    label = entry.label or "Sensor"
                    current = entry.current
                    
                    # Temperature status
                    if hasattr(entry, 'critical') and entry.critical and current >= entry.critical:
                        temp_status = " [CRITICAL]"
                    elif hasattr(entry, 'high') and entry.high and current >= entry.high:
                        temp_status = " [HIGH]"
                    elif current >= 75:  # General high temp threshold
                        temp_status = " [HIGH]"
                    else:
                        temp_status = " [OK]"
                    
                    temp_info += f"\n  {label}: {current:.1f}°C{temp_status}"
            
            return temp_info
            
        except Exception as e:
            return "Error retrieving temperature information"
    
    def analyze_system_with_ai(self):
        """Use Groq AI to analyze current system state"""
        if not self.groq_client:
            return "AI analysis not available (Groq API key required)"
        
        try:
            # Gather system data
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Prepare data for AI analysis
            system_data = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage_percent': (disk.used / disk.total) * 100,
                'uptime': self.get_uptime(),
                'process_count': len(psutil.pids()),
                'alerts': len([a for a in self.get_system_alerts().split('\n') if 'WARNING' in a or 'CRITICAL' in a])
            }
            
            # Add battery if available
            try:
                battery = psutil.sensors_battery()
                if battery:
                    system_data['battery_percent'] = battery.percent
                    system_data['on_battery'] = not battery.power_plugged
            except:
                pass
            
            system_prompt = f"""You are an AI system administrator analyzing computer performance. Based on the current system metrics, provide a concise analysis with:

1. Overall system health assessment
2. Performance bottlenecks or concerns
3. Specific recommendations for optimization
4. Any immediate actions needed

Current system metrics:
{json.dumps(system_data, indent=2)}

Keep response under 200 words and be practical."""
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Analyze my system performance"}
                ],
                model=self.groq_model,
                max_tokens=250,
                temperature=0.3
            )
            
            ai_analysis = response.choices[0].message.content.strip()
            
            return f"AI SYSTEM ANALYSIS\n{'-' * 50}\n{ai_analysis}"
            
        except Exception as e:
            self.logger.error(f"AI analysis error: {e}")
            return "Error performing AI system analysis"
    
    def get_uptime(self):
        """Get formatted system uptime"""
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
    
    def get_quick_status(self):
        """Get one-line system status"""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            status = f"CPU: {cpu:.1f}% | RAM: {memory.percent:.1f}% | Available: {memory.available / (1024**3):.1f}GB"
            
            # Add battery if available
            try:
                battery = psutil.sensors_battery()
                if battery:
                    power_source = "AC" if battery.power_plugged else "BAT"
                    status += f" | {power_source}: {battery.percent}%"
            except:
                pass
            
            return status
            
        except Exception as e:
            return "System status unavailable"
    
    def get_historical_data(self, metric='cpu', hours=1):
        """Get historical performance data"""
        if metric == 'cpu' and self.cpu_history:
            data = list(self.cpu_history)
            cutoff = datetime.now() - timedelta(hours=hours)
            recent_data = [d for d in data if d['time'] >= cutoff]
            
            if recent_data:
                avg = sum(d['value'] for d in recent_data) / len(recent_data)
                max_val = max(d['value'] for d in recent_data)
                min_val = min(d['value'] for d in recent_data)
                
                return f"CPU (last {hours}h): Avg {avg:.1f}%, Max {max_val:.1f}%, Min {min_val:.1f}%"
        
        return f"No historical data available for {metric}"
    
    def export_system_report(self, filepath=None):
        """Export comprehensive system report to file"""
        try:
            if not filepath:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = f"system_report_{timestamp}.txt"
            
            report = f"""SYSTEM REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

{self.get_system_overview()}

{'=' * 80}
{self.get_performance_status(detailed=True)}

{'=' * 80}
{self.get_storage_status()}

{'=' * 80}
{self.get_network_status()}

{'=' * 80}
{self.get_top_processes(15)}

{'=' * 80}
{self.get_system_alerts()}

{'=' * 80}
{self.get_battery_status()}

{'=' * 80}
{self.get_temperature_status()}
"""
            
            if self.groq_client:
                report += f"\n{'=' * 80}\n{self.analyze_system_with_ai()}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return f"System report saved to {filepath}"
            
        except Exception as e:
            self.logger.error(f"Export report error: {e}")
            return f"Error exporting report: {e}"


# Quick utility functions for common tasks
def quick_status():
    """Quick system status check"""
    monitor = SystemMonitor()
    return monitor.get_quick_status()


def performance_check():
    """Quick performance check"""
    monitor = SystemMonitor()
    return monitor.get_performance_status()


def system_health():
    """Complete system health check"""
    monitor = SystemMonitor()
    return f"{monitor.get_performance_status()}\n\n{monitor.get_system_alerts()}"


if __name__ == "__main__":
    # Demo the enhanced system monitor
    monitor = SystemMonitor()
    
    print("Enhanced System Monitor Demo")
    print("=" * 50)
    
    # Test intent classification
    test_commands = [
        "show me cpu usage",
        "what's the weather like?",
        "check system performance",
        "tell me a joke",
        "memory usage status",
        "how are you today?"
    ]
    
    print("\nTesting Intent Classification:")
    for cmd in test_commands:
        intent = monitor.classify_intent(cmd)
        print(f"'{cmd}' -> {intent}")
    
    print("\n" + "=" * 50)
    print("System Overview:")
    print(monitor.get_system_overview())
    
    print("\n" + "=" * 50)
    print("Performance Status:")
    print(monitor.get_performance_status())
    
    print("\n" + "=" * 50)
    print("System Alerts:")
    print(monitor.get_system_alerts())
    
    if monitor.groq_client:
        print("\n" + "=" * 50)
        print("AI Analysis:")
        print(monitor.analyze_system_with_ai())
    
    print(f"\nQuick Status: {monitor.get_quick_status()}")
