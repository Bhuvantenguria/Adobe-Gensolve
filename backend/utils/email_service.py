from flask_mail import Mail, Message
from flask import current_app
import os
from datetime import datetime

class EmailService:
    def __init__(self, app):
        """Initialize email service with Flask app"""
        self.mail = Mail(app)
        
    def send_email(self, to_email, subject, body, html_body=None):
        """Send email"""
        try:
            msg = Message(
                subject=subject,
                recipients=[to_email],
                sender=current_app.config['MAIL_USERNAME']
            )
            
            msg.body = body
            if html_body:
                msg.html = html_body
                
            self.mail.send(msg)
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email, user_name):
        """Send welcome email to new user"""
        subject = "Welcome to Adobe-GenSolve! 🎨"
        
        body = f"""
        Hi {user_name},
        
        Welcome to Adobe-GenSolve! We're excited to have you on board.
        
        Adobe-GenSolve is your creative platform for:
        • Drawing and sketching with advanced tools
        • Image processing and shape detection
        • Converting drawings to code
        • Sharing your creations with the community
        
        Get started by:
        1. Exploring our drawing tools
        2. Uploading images for processing
        3. Joining our community challenges
        
        If you have any questions, feel free to reach out to our support team.
        
        Happy creating!
        The Adobe-GenSolve Team
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎨 Welcome to Adobe-GenSolve!</h1>
                    <p>Your Creative Journey Starts Here</p>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>Welcome to Adobe-GenSolve! We're excited to have you join our creative community.</p>
                    
                    <h3>What you can do with Adobe-GenSolve:</h3>
                    <div class="feature">
                        <strong>🎨 Advanced Drawing Tools</strong><br>
                        Create beautiful sketches with our professional-grade drawing tools
                    </div>
                    <div class="feature">
                        <strong>🔍 Smart Shape Detection</strong><br>
                        Automatically detect and analyze shapes in your images
                    </div>
                    <div class="feature">
                        <strong>💻 Code Generation</strong><br>
                        Convert your drawings to HTML, CSS, and React components
                    </div>
                    <div class="feature">
                        <strong>🌐 Community Sharing</strong><br>
                        Share your creations and get inspired by others
                    </div>
                    
                    <h3>Get Started:</h3>
                    <ol>
                        <li>Explore our drawing canvas</li>
                        <li>Try our image processing features</li>
                        <li>Join community challenges</li>
                        <li>Share your first creation</li>
                    </ol>
                    
                    <a href="http://localhost:3000" class="button">Start Creating Now</a>
                    
                    <p>If you have any questions, our support team is here to help!</p>
                    
                    <p>Happy creating!<br>
                    <strong>The Adobe-GenSolve Team</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_password_reset_email(self, user_email, reset_token, user_name):
        """Send password reset email"""
        subject = "Reset Your Adobe-GenSolve Password"
        
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        
        body = f"""
        Hi {user_name},
        
        You requested to reset your password for Adobe-GenSolve.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        The Adobe-GenSolve Team
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>We received a request to reset your password for Adobe-GenSolve.</p>
                    
                    <a href="{reset_url}" class="button">Reset Password</a>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong>
                        <ul>
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this, please ignore this email</li>
                            <li>Never share this link with anyone</li>
                        </ul>
                    </div>
                    
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                    
                    <p>Best regards,<br>
                    <strong>The Adobe-GenSolve Team</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_processing_complete_email(self, user_email, user_name, processing_type, download_url):
        """Send email when processing is complete"""
        subject = f"Your {processing_type} Processing is Complete! ✅"
        
        body = f"""
        Hi {user_name},
        
        Great news! Your {processing_type} processing has been completed successfully.
        
        You can download your results here:
        {download_url}
        
        Thank you for using Adobe-GenSolve!
        
        Best regards,
        The Adobe-GenSolve Team
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .success {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Processing Complete!</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    
                    <div class="success">
                        <strong>🎉 Success!</strong> Your {processing_type} processing has been completed successfully.
                    </div>
                    
                    <p>Your files are ready for download:</p>
                    
                    <a href="{download_url}" class="button">Download Results</a>
                    
                    <p>What's included in your download:</p>
                    <ul>
                        <li>Processed images</li>
                        <li>SVG files</li>
                        <li>CSV data</li>
                        <li>Analysis reports</li>
                    </ul>
                    
                    <p>Thank you for using Adobe-GenSolve!</p>
                    
                    <p>Best regards,<br>
                    <strong>The Adobe-GenSolve Team</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_community_notification(self, user_email, user_name, notification_type, content):
        """Send community notification email"""
        subject = f"Adobe-GenSolve Community Update: {notification_type}"
        
        body = f"""
        Hi {user_name},
        
        You have a new community update from Adobe-GenSolve:
        
        {content}
        
        Visit our platform to see more details.
        
        Best regards,
        The Adobe-GenSolve Team
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #17a2b8; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .notification {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #17a2b8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌐 Community Update</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    
                    <div class="notification">
                        <h3>{notification_type}</h3>
                        <p>{content}</p>
                    </div>
                    
                    <a href="http://localhost:3000/community" class="button">View Community</a>
                    
                    <p>Best regards,<br>
                    <strong>The Adobe-GenSolve Team</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_weekly_digest(self, user_email, user_name, digest_data):
        """Send weekly digest email"""
        subject = "Your Adobe-GenSolve Weekly Digest 📊"
        
        body = f"""
        Hi {user_name},
        
        Here's your weekly Adobe-GenSolve digest:
        
        📈 Your Activity:
        - Drawings created: {digest_data.get('drawings_created', 0)}
        - Images processed: {digest_data.get('images_processed', 0)}
        - Community interactions: {digest_data.get('interactions', 0)}
        
        🏆 Community Highlights:
        {digest_data.get('community_highlights', 'No highlights this week')}
        
        🎯 This Week's Challenge:
        {digest_data.get('weekly_challenge', 'No challenge this week')}
        
        Keep creating amazing things!
        
        Best regards,
        The Adobe-GenSolve Team
        """
        
        return self.send_email(user_email, subject, body) 