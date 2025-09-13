#!/usr/bin/env python3
"""
Email Handler - Complete email automation system
"""

import smtplib
import imaplib
import email
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

class EmailHandler:
    def __init__(self):
        self.logger = setup_logger()
        
        # Email configuration
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # SMTP servers for common providers
        self.smtp_servers = {
            'gmail.com': ('smtp.gmail.com', 587),
            'outlook.com': ('smtp-mail.outlook.com', 587),
            'hotmail.com': ('smtp-mail.outlook.com', 587),
            'yahoo.com': ('smtp.mail.yahoo.com', 587),
            'icloud.com': ('smtp.mail.me.com', 587)
        }
        
        # IMAP servers for reading emails
        self.imap_servers = {
            'gmail.com': 'imap.gmail.com',
            'outlook.com': 'imap-mail.outlook.com',
            'hotmail.com': 'imap-mail.outlook.com',
            'yahoo.com': 'imap.mail.yahoo.com',
            'icloud.com': 'imap.mail.me.com'
        }
        
        print("Email Handler initialized!")
    
    def handle_email_request(self, command):
        """Process email-related commands"""
        command = command.lower()
        
        if "send email" in command or "send mail" in command:
            return self.send_email_wizard(command)
        elif "check email" in command or "read email" in command:
            return self.check_emails()
        elif "unread" in command:
            return self.get_unread_count()
        else:
            return "I can help you send emails or check your inbox. What would you like to do?"
    
    def send_email_wizard(self, command):
        """Interactive email sending wizard"""
        try:
            if not self.email_address or not self.email_password:
                return self.setup_instructions()
            
            # For hackathon - simplified email sending
            # In production, you'd want a more interactive approach
            return "Email sending wizard started! For now, use the send_email() method directly with recipient, subject, and message."
            
        except Exception as e:
            self.logger.error(f"Email wizard error: {e}")
            return "Error starting email wizard."
    
    def send_email(self, to_email, subject, body, attachments=None):
        """Send an email"""
        try:
            if not self.email_address or not self.email_password:
                return self.setup_instructions()
            
            # Determine SMTP server
            domain = self.email_address.split('@')[1]
            smtp_config = self.smtp_servers.get(domain)
            
            if not smtp_config:
                return f"Unsupported email provider: {domain}"
            
            smtp_server, smtp_port = smtp_config
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        self.add_attachment(msg, file_path)
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            return f"✅ Email sent successfully to {to_email}"
            
        except smtplib.SMTPAuthenticationError:
            return "❌ Email authentication failed. Please check your email credentials."
        except smtplib.SMTPException as e:
            return f"❌ SMTP error: {str(e)}"
        except Exception as e:
            self.logger.error(f"Send email error: {e}")
            return f"❌ Error sending email: {str(e)}"
    
    def add_attachment(self, msg, file_path):
        """Add attachment to email"""
        try:
            file_path = Path(file_path)
            
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path.name}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            self.logger.error(f"Attachment error: {e}")
    
    def check_emails(self, count=5):
        """Check recent emails"""
        try:
            if not self.email_address or not self.email_password:
                return self.setup_instructions()
            
            # Determine IMAP server
            domain = self.email_address.split('@')[1]
            imap_server = self.imap_servers.get(domain)
            
            if not imap_server:
                return f"Cannot check emails for {domain}"
            
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(self.email_address, self.email_password)
            mail.select('inbox')
            
            # Search for recent emails
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            
            if not email_ids:
                mail.logout()
                return "📧 No emails found in inbox."
            
            # Get recent emails
            recent_emails = []
            for email_id in email_ids[-count:]:  # Get last N emails
                result, data = mail.fetch(email_id, '(RFC822)')
                raw_email = data[0][1]
                
                email_message = email.message_from_bytes(raw_email)
                
                # Extract email info
                sender = email_message.get('From', 'Unknown sender')
                subject = email_message.get('Subject', 'No subject')
                date = email_message.get('Date', 'Unknown date')
                
                # Parse date
                try:
                    parsed_date = email.utils.parsedate_to_datetime(date)
                    formatted_date = parsed_date.strftime('%m/%d %H:%M')
                except:
                    formatted_date = 'Unknown time'
                
                recent_emails.append({
                    'sender': sender,
                    'subject': subject,
                    'date': formatted_date
                })
            
            mail.logout()
            
            # Format response
            if recent_emails:
                response = f"📧 Recent Emails ({len(recent_emails)}):\\n\\n"
                
                for i, email_info in enumerate(reversed(recent_emails), 1):  # Most recent first
                    sender = email_info['sender'].split('<')[0].strip()[:30]  # Clean sender name
                    subject = email_info['subject'][:50]  # Truncate long subjects
                    date = email_info['date']
                    
                    response += f"{i}. From: {sender}\\n"
                    response += f"   Subject: {subject}\\n"
                    response += f"   Date: {date}\\n\\n"
                
                return response
            else:
                return "📧 No recent emails found."
                
        except imaplib.IMAP4.error as e:
            return f"❌ Email server error: {str(e)}"
        except Exception as e:
            self.logger.error(f"Check emails error: {e}")
            return "❌ Error checking emails. Please verify your email settings."
    
    def get_unread_count(self):
        """Get count of unread emails"""
        try:
            if not self.email_address or not self.email_password:
                return self.setup_instructions()
            
            domain = self.email_address.split('@')[1]
            imap_server = self.imap_servers.get(domain)
            
            if not imap_server:
                return f"Cannot check unread emails for {domain}"
            
            # Connect and check unread
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(self.email_address, self.email_password)
            mail.select('inbox')
            
            # Search for unread emails
            result, data = mail.search(None, 'UNSEEN')
            unread_ids = data[0].split()
            
            mail.logout()
            
            unread_count = len(unread_ids)
            
            if unread_count == 0:
                return "📧 No unread emails."
            elif unread_count == 1:
                return "📧 You have 1 unread email."
            else:
                return f"📧 You have {unread_count} unread emails."
                
        except Exception as e:
            self.logger.error(f"Unread count error: {e}")
            return "❌ Error checking unread emails."
    
    def send_quick_notification(self, recipient, message):
        """Send a quick notification email"""
        subject = f"Notification from Jarvis - {datetime.now().strftime('%H:%M')}"
        body = f"Jarvis Notification:\\n\\n{message}\\n\\nSent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_email(recipient, subject, body)
    
    def send_system_alert(self, alert_message):
        """Send system alert email to configured recipient"""
        alert_recipient = os.getenv('ALERT_EMAIL', self.email_address)
        
        if alert_recipient:
            subject = "🚨 System Alert from Jarvis"
            body = f"System Alert:\\n\\n{alert_message}\\n\\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return self.send_email(alert_recipient, subject, body)
        else:
            return "No alert recipient configured."
    
    def setup_instructions(self):
        """Provide setup instructions for email"""
        instructions = """📧 Email Setup Required\\n\\n"""
        instructions += """To use email features, add these to your .env file:\\n\\n"""
        instructions += """EMAIL_ADDRESS=your_email@gmail.com\\n"""
        instructions += """EMAIL_PASSWORD=your_app_password\\n\\n"""
        instructions += """📝 Important Notes:\\n"""
        instructions += """• For Gmail: Use App Password, not regular password\\n"""
        instructions += """• Enable 2-factor authentication first\\n"""
        instructions += """• Generate App Password in Google Account settings\\n"""
        instructions += """• For other providers: Check if app passwords are required\\n\\n"""
        instructions += """🔒 Supported providers: Gmail, Outlook, Yahoo, iCloud"""
        
        return instructions
    
    def test_email_connection(self):
        """Test email connection"""
        try:
            if not self.email_address or not self.email_password:
                return "❌ Email credentials not configured."
            
            domain = self.email_address.split('@')[1]
            smtp_config = self.smtp_servers.get(domain)
            
            if not smtp_config:
                return f"❌ Unsupported email provider: {domain}"
            
            smtp_server, smtp_port = smtp_config
            
            # Test SMTP connection
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.quit()
            
            return f"✅ Email connection successful for {self.email_address}"
            
        except smtplib.SMTPAuthenticationError:
            return "❌ Authentication failed. Check email credentials."
        except Exception as e:
            return f"❌ Connection test failed: {str(e)}"
