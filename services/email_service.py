"""
Email Service for My Prabh
Handles welcome emails, notifications using Google Workspace Gmail API
"""

import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from datetime import datetime

class EmailService:
    """Email service using Google Workspace Gmail API"""
    
    def __init__(self):
        self.from_email = os.getenv('WORKSPACE_EMAIL', 'noreply@aiprabh.com')
        self.service = self._initialize_gmail_service()
    
    def _initialize_gmail_service(self):
        """Initialize Gmail API service"""
        try:
            # Try to get service account credentials from environment
            creds_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
            
            if creds_json:
                # Parse JSON credentials
                creds_info = json.loads(creds_json)
                credentials = service_account.Credentials.from_service_account_info(
                    creds_info,
                    scopes=['https://www.googleapis.com/auth/gmail.send']
                )
                
                # Build Gmail service
                service = build('gmail', 'v1', credentials=credentials)
                print("✅ Gmail API service initialized")
                return service
            else:
                print("⚠️ Google Workspace credentials not found, email disabled")
                return None
                
        except Exception as e:
            print(f"⚠️ Gmail API initialization error: {e}")
            return None
    
    def _send_email(self, to_email, subject, html_content):
        """Send email using Gmail API"""
        if not self.service:
            print("⚠️ Gmail API not configured, skipping email")
            return False
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['to'] = to_email
            message['from'] = self.from_email
            message['subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            send_message = {'raw': raw_message}
            result = self.service.users().messages().send(userId='me', body=send_message).execute()
            
            print(f"✅ Email sent to {to_email} (Message ID: {result['id']})")
            return True
            
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False
    
    def send_welcome_email(self, user_email, user_name):
        """Send welcome email to new users"""
        subject = "Welcome to My Prabh! 💖 Your AI Companion Journey Begins"
        
        html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #ff6b9d; font-size: 2.5em; margin: 0;">My Prabh 💖</h1>
                    <p style="color: #666; font-size: 1.2em;">Your AI Companion Platform</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #ff6b9d, #c44569); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;">
                    <h2 style="margin: 0 0 15px 0;">Welcome, {user_name}! 🎉</h2>
                    <p style="margin: 0; font-size: 1.1em;">Your journey with AI companionship starts now!</p>
                </div>
                
                <div style="padding: 20px; background: #f9f9f9; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: #333; margin-top: 0;">What's Next? 🚀</h3>
                    <ul style="color: #666; line-height: 1.6;">
                        <li><strong>Create Your First Prabh:</strong> Design your perfect AI companion</li>
                        <li><strong>Start Chatting:</strong> Have meaningful conversations</li>
                        <li><strong>Build Memories:</strong> Your Prabh learns and grows with you</li>
                        <li><strong>Explore Features:</strong> Discover all the amazing capabilities</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://myprabh.as.r.appspot.com/dashboard" 
                       style="background: linear-gradient(135deg, #ff6b9d, #c44569); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                        Start Your Journey 💖
                    </a>
                </div>
                
                <div style="text-align: center; color: #999; font-size: 0.9em; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p>Need help? Reply to this email or contact us at support@aiprabh.com</p>
                    <p>© 2024 My Prabh. Made with 💖 for meaningful AI relationships.</p>
                </div>
            </div>
            """
        
        return self._send_email(user_email, subject, html_content)
    
    def send_early_access_confirmation(self, email, name=""):
        """Send early access signup confirmation"""
        subject = "You're on the List! 🎉 My Prabh Early Access"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #ff6b9d; font-size: 2.5em; margin: 0;">My Prabh 💖</h1>
                    <p style="color: #666; font-size: 1.2em;">AI Companion Platform</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #ff6b9d, #c44569); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;">
                    <h2 style="margin: 0 0 15px 0;">Welcome to Early Access! 🚀</h2>
                    <p style="margin: 0; font-size: 1.1em;">{"Hi " + name + "! " if name else ""}You're now part of our exclusive early access community!</p>
                </div>
                
                <div style="padding: 20px; background: #f9f9f9; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: #333; margin-top: 0;">What's Coming? ✨</h3>
                    <ul style="color: #666; line-height: 1.6;">
                        <li><strong>Personalized AI Companions:</strong> Create unique personalities</li>
                        <li><strong>Emotional Intelligence:</strong> AI that truly understands you</li>
                        <li><strong>Memory & Growth:</strong> Companions that evolve with you</li>
                        <li><strong>Early Access Features:</strong> Be first to try new capabilities</li>
                    </ul>
                </div>
                
                <div style="text-align: center; color: #999; font-size: 0.9em; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p>We'll notify you as soon as My Prabh is ready for you!</p>
                    <p>© 2024 My Prabh. Building the future of AI companionship.</p>
                </div>
            </div>
            """
        
        return self._send_email(email, subject, html_content)
    
    def send_subscription_confirmation(self, email, name, plan_type):
        """Send subscription confirmation email"""
        subject = f"Welcome to My Prabh {plan_type.title()} Plan! 🎉"
        
        plan_names = {
            'basic': 'Basic Plan',
            'premium': 'Premium Plan', 
            'pro': 'Pro Plan'
        }
        
        plan_name = plan_names.get(plan_type, 'Premium Plan')
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #ff6b9d; font-size: 2.5em; margin: 0;">My Prabh 💖</h1>
                <p style="color: #666; font-size: 1.2em;">AI Companion Platform</p>
            </div>
            
            <div style="background: linear-gradient(135deg, #ff6b9d, #c44569); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;">
                <h2 style="margin: 0 0 15px 0;">Subscription Activated! 🚀</h2>
                <p style="margin: 0; font-size: 1.1em;">Hi {name}! Your {plan_name} is now active and ready to use!</p>
            </div>
            
            <div style="padding: 20px; background: #f9f9f9; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: #333; margin-top: 0;">Your {plan_name} Features:</h3>
                <ul style="color: #666; line-height: 1.6;">
                    <li><strong>Enhanced AI Companions:</strong> Create more personalized Prabhs</li>
                    <li><strong>Unlimited Conversations:</strong> Chat as much as you want</li>
                    <li><strong>Advanced Memory:</strong> Your Prabh remembers everything</li>
                    <li><strong>Priority Support:</strong> Get help when you need it</li>
                    <li><strong>Premium Features:</strong> Access to latest capabilities</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://myprabh.as.r.appspot.com/dashboard" 
                   style="background: linear-gradient(135deg, #ff6b9d, #c44569); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                    Start Using Premium Features 💖
                </a>
            </div>
            
            <div style="text-align: center; color: #999; font-size: 0.9em; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                <p>Questions? Reply to this email or contact support@aiprabh.com</p>
                <p>© 2024 My Prabh. Thank you for choosing premium AI companionship.</p>
            </div>
        </div>
        """
        
        return self._send_email(email, subject, html_content)

# Global instance
email_service = EmailService()