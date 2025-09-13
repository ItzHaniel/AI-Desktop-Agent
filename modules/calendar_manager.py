#!/usr/bin/env python3
"""
Calendar Manager - Complete calendar and reminder system
"""

import datetime
import json
from pathlib import Path
from utils.logger import setup_logger

# Optional: Windows Outlook integration
try:
    import win32com.client as win32
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False

# Optional: Google Calendar integration
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False

class CalendarManager:
    def __init__(self):
        self.logger = setup_logger()
        
        # Initialize Outlook if available
        if OUTLOOK_AVAILABLE:
            self.setup_outlook()
        else:
            self.outlook = None
        
        # Local calendar storage
        self.calendar_file = Path("data") / "local_calendar.json"
        self.reminders_file = Path("data") / "reminders.json"
        
        # Load local calendar
        self.local_events = self.load_local_calendar()
        self.reminders = self.load_reminders()
        
        print("Calendar Manager initialized!")
    
    def setup_outlook(self):
        """Initialize Outlook connection"""
        try:
            self.outlook = win32.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            print("Outlook integration enabled!")
        except Exception as e:
            self.logger.error(f"Outlook setup error: {e}")
            self.outlook = None
    
    def handle_calendar_request(self, command):
        """Process calendar-related commands"""
        command = command.lower()
        
        if "schedule" in command or "meeting" in command or "appointment" in command:
            return self.schedule_event(command)
        elif "reminder" in command or "remind" in command:
            return self.set_reminder(command)
        elif "events" in command or "appointments" in command or "calendar" in command:
            if "today" in command:
                return self.get_today_events()
            elif "tomorrow" in command:
                return self.get_tomorrow_events()
            elif "week" in command:
                return self.get_week_events()
            else:
                return self.get_today_events()
        elif "delete" in command or "cancel" in command:
            return self.cancel_event(command)
        elif "list reminders" in command:
            return self.list_reminders()
        else:
            return "I can help you schedule events, set reminders, or check your calendar. What would you like to do?"
    
    def schedule_event(self, command):
        """Schedule a new event"""
        try:
            # Extract event details from command
            event_details = self.parse_event_command(command)
            
            # Try Outlook first, then local calendar
            if self.outlook:
                result = self.create_outlook_event(event_details)
            else:
                result = self.create_local_event(event_details)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Event scheduling error: {e}")
            return "Error scheduling event. Please try again."
    
    def parse_event_command(self, command):
        """Parse event details from natural language command"""
        now = datetime.datetime.now()
        
        # Default event details
        event = {
            'title': 'Meeting scheduled by Jarvis',
            'start_time': now + datetime.timedelta(hours=1),
            'duration': 60,  # minutes
            'description': f"Event created from command: {command}"
        }
        
        # Parse time expressions
        if "tomorrow" in command:
            tomorrow = now + datetime.timedelta(days=1)
            if "morning" in command:
                event['start_time'] = tomorrow.replace(hour=9, minute=0, second=0)
            elif "afternoon" in command:
                event['start_time'] = tomorrow.replace(hour=14, minute=0, second=0)
            elif "evening" in command:
                event['start_time'] = tomorrow.replace(hour=18, minute=0, second=0)
            else:
                event['start_time'] = tomorrow.replace(hour=10, minute=0, second=0)
        
        elif "next week" in command:
            next_week = now + datetime.timedelta(days=7)
            event['start_time'] = next_week.replace(hour=10, minute=0, second=0)
        
        elif "monday" in command:
            event['start_time'] = self.get_next_weekday(0, 10, 0)  # Monday
        elif "tuesday" in command:
            event['start_time'] = self.get_next_weekday(1, 10, 0)  # Tuesday
        elif "wednesday" in command:
            event['start_time'] = self.get_next_weekday(2, 10, 0)  # Wednesday
        elif "thursday" in command:
            event['start_time'] = self.get_next_weekday(3, 10, 0)  # Thursday
        elif "friday" in command:
            event['start_time'] = self.get_next_weekday(4, 10, 0)  # Friday
        
        # Parse duration
        if "30 minutes" in command or "half hour" in command:
            event['duration'] = 30
        elif "2 hours" in command:
            event['duration'] = 120
        elif "hour" in command and "2" not in command:
            event['duration'] = 60
        
        # Extract title/subject
        if "meeting" in command:
            if "team" in command:
                event['title'] = "Team Meeting"
            elif "client" in command:
                event['title'] = "Client Meeting"
            elif "project" in command:
                event['title'] = "Project Meeting"
            else:
                event['title'] = "Meeting"
        elif "call" in command:
            event['title'] = "Phone Call"
        elif "appointment" in command:
            event['title'] = "Appointment"
        
        return event
    
    def get_next_weekday(self, weekday, hour, minute):
        """Get next occurrence of a specific weekday"""
        today = datetime.datetime.now()
        days_ahead = weekday - today.weekday()
        
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        target_date = today + datetime.timedelta(days=days_ahead)
        return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def create_outlook_event(self, event_details):
        """Create event in Outlook"""
        try:
            appointment = self.outlook.CreateItem(1)  # olAppointmentItem
            
            appointment.Start = event_details['start_time']
            appointment.Duration = event_details['duration']
            appointment.Subject = event_details['title']
            appointment.Body = event_details['description']
            appointment.ReminderSet = True
            appointment.ReminderMinutesBeforeStart = 15
            
            appointment.Save()
            
            formatted_time = event_details['start_time'].strftime('%Y-%m-%d at %H:%M')
            return f"✅ '{event_details['title']}' scheduled for {formatted_time} in Outlook"
            
        except Exception as e:
            self.logger.error(f"Outlook event creation error: {e}")
            # Fallback to local calendar
            return self.create_local_event(event_details)
    
    def create_local_event(self, event_details):
        """Create event in local calendar"""
        try:
            event_id = len(self.local_events) + 1
            
            local_event = {
                'id': event_id,
                'title': event_details['title'],
                'start_time': event_details['start_time'].isoformat(),
                'duration': event_details['duration'],
                'description': event_details['description'],
                'created_at': datetime.datetime.now().isoformat()
            }
            
            self.local_events.append(local_event)
            self.save_local_calendar()
            
            formatted_time = event_details['start_time'].strftime('%Y-%m-%d at %H:%M')
            return f"✅ '{event_details['title']}' scheduled for {formatted_time} (Local Calendar)"
            
        except Exception as e:
            self.logger.error(f"Local event creation error: {e}")
            return "Error creating local event."
    
    def set_reminder(self, command):
        """Set a reminder"""
        try:
            reminder_details = self.parse_reminder_command(command)
            
            reminder_id = len(self.reminders) + 1
            reminder = {
                'id': reminder_id,
                'message': reminder_details['message'],
                'remind_time': reminder_details['remind_time'].isoformat(),
                'created_at': datetime.datetime.now().isoformat(),
                'completed': False
            }
            
            self.reminders.append(reminder)
            self.save_reminders()
            
            formatted_time = reminder_details['remind_time'].strftime('%Y-%m-%d at %H:%M')
            return f"⏰ Reminder set: '{reminder_details['message']}' for {formatted_time}"
            
        except Exception as e:
            self.logger.error(f"Reminder creation error: {e}")
            return "Error setting reminder."
    
    def parse_reminder_command(self, command):
        """Parse reminder details from command"""
        now = datetime.datetime.now()
        
        # Default reminder
        reminder = {
            'message': 'Reminder from Jarvis',
            'remind_time': now + datetime.timedelta(hours=1)
        }
        
        # Parse time expressions
        if "tomorrow" in command:
            tomorrow = now + datetime.timedelta(days=1)
            reminder['remind_time'] = tomorrow.replace(hour=9, minute=0, second=0)
        elif "in 30 minutes" in command:
            reminder['remind_time'] = now + datetime.timedelta(minutes=30)
        elif "in an hour" in command or "in 1 hour" in command:
            reminder['remind_time'] = now + datetime.timedelta(hours=1)
        elif "in 2 hours" in command:
            reminder['remind_time'] = now + datetime.timedelta(hours=2)
        elif "tonight" in command:
            reminder['remind_time'] = now.replace(hour=20, minute=0, second=0)
        
        # Extract message
        words_to_remove = ["remind", "me", "to", "about", "that", "tomorrow", "tonight", "in", "minutes", "hour", "hours"]
        words = command.split()
        message_words = [word for word in words if word not in words_to_remove]
        
        if message_words:
            reminder['message'] = " ".join(message_words).title()
        
        return reminder
    
    def get_today_events(self):
        """Get today's events"""
        try:
            today = datetime.date.today()
            events = []
            
            # Get Outlook events if available
            if self.outlook:
                outlook_events = self.get_outlook_events(today)
                events.extend(outlook_events)
            
            # Get local events
            local_events = self.get_local_events(today)
            events.extend(local_events)
            
            if events:
                result = f"📅 Events for {today.strftime('%A, %B %d, %Y')}:\\n\\n"
                
                # Sort events by time
                events.sort(key=lambda x: x['start_time'])
                
                for event in events:
                    start_time = event['start_time'].strftime('%H:%M')
                    result += f"• {start_time} - {event['title']}\\n"
                    if event.get('description'):
                        result += f"  📝 {event['description'][:50]}...\\n"
                    result += "\\n"
                
                return result
            else:
                return f"📅 No events scheduled for today ({today.strftime('%A, %B %d')})."
                
        except Exception as e:
            self.logger.error(f"Get today events error: {e}")
            return "Error retrieving today's events."
    
    def get_tomorrow_events(self):
        """Get tomorrow's events"""
        try:
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            events = []
            
            # Get Outlook events if available
            if self.outlook:
                outlook_events = self.get_outlook_events(tomorrow)
                events.extend(outlook_events)
            
            # Get local events
            local_events = self.get_local_events(tomorrow)
            events.extend(local_events)
            
            if events:
                result = f"📅 Events for {tomorrow.strftime('%A, %B %d, %Y')}:\\n\\n"
                
                events.sort(key=lambda x: x['start_time'])
                
                for event in events:
                    start_time = event['start_time'].strftime('%H:%M')
                    result += f"• {start_time} - {event['title']}\\n"
                
                return result
            else:
                return f"📅 No events scheduled for tomorrow ({tomorrow.strftime('%A, %B %d')})."
                
        except Exception as e:
            self.logger.error(f"Get tomorrow events error: {e}")
            return "Error retrieving tomorrow's events."
    
    def get_outlook_events(self, target_date):
        """Get events from Outlook for specific date"""
        try:
            if not self.outlook:
                return []
            
            calendar = self.namespace.GetDefaultFolder(9)  # olFolderCalendar
            appointments = calendar.Items
            appointments.Sort("[Start]")
            
            events = []
            for appointment in appointments:
                appt_date = appointment.Start.date()
                if appt_date == target_date:
                    events.append({
                        'title': appointment.Subject,
                        'start_time': appointment.Start,
                        'description': appointment.Body[:100] if appointment.Body else '',
                        'source': 'Outlook'
                    })
            
            return events
            
        except Exception as e:
            self.logger.error(f"Outlook events error: {e}")
            return []
    
    def get_local_events(self, target_date):
        """Get events from local calendar for specific date"""
        try:
            events = []
            
            for event in self.local_events:
                event_date = datetime.datetime.fromisoformat(event['start_time']).date()
                if event_date == target_date:
                    events.append({
                        'title': event['title'],
                        'start_time': datetime.datetime.fromisoformat(event['start_time']),
                        'description': event.get('description', ''),
                        'source': 'Local'
                    })
            
            return events
            
        except Exception as e:
            self.logger.error(f"Local events error: {e}")
            return []
    
    def list_reminders(self):
        """List active reminders"""
        try:
            active_reminders = [r for r in self.reminders if not r.get('completed', False)]
            
            if active_reminders:
                result = f"⏰ Active Reminders ({len(active_reminders)}):\\n\\n"
                
                for reminder in sorted(active_reminders, key=lambda x: x['remind_time']):
                    remind_time = datetime.datetime.fromisoformat(reminder['remind_time'])
                    formatted_time = remind_time.strftime('%m-%d %H:%M')
                    result += f"• {formatted_time} - {reminder['message']}\\n"
                
                return result
            else:
                return "⏰ No active reminders."
                
        except Exception as e:
            self.logger.error(f"List reminders error: {e}")
            return "Error retrieving reminders."
    
    def load_local_calendar(self):
        """Load local calendar from file"""
        try:
            if self.calendar_file.exists():
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Load calendar error: {e}")
            return []
    
    def save_local_calendar(self):
        """Save local calendar to file"""
        try:
            self.calendar_file.parent.mkdir(exist_ok=True)
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump(self.local_events, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Save calendar error: {e}")
    
    def load_reminders(self):
        """Load reminders from file"""
        try:
            if self.reminders_file.exists():
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Load reminders error: {e}")
            return []
    
    def save_reminders(self):
        """Save reminders to file"""
        try:
            self.reminders_file.parent.mkdir(exist_ok=True)
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Save reminders error: {e}")
