import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass

def test_email_sending():
    # Email configuration
    sender_email = "newsletter@efels.com"
    recipient_email = input("Enter your personal email to receive the test: ")
    smtp_server = "mail.efels.com"
    smtp_port = 465  # SSL port
    smtp_username = "newsletter@efels.com"
    smtp_password = getpass.getpass("Enter your email password: ")  # More secure password input
    
    # Create message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'Test Email from Newsletter System'
    
    # Email body
    body = """
    <html>
    <body>
        <h2>Test Email</h2>
        <p>This is a test email to verify SMTP settings for the newsletter system.</p>
        <p>If you're receiving this, it means your email configuration is working correctly!</p>
    </body>
    </html>
    """
    
    message.attach(MIMEText(body, 'html'))
    
    print("Attempting to send email...")
    try:
        # Connect to server (using SSL)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            print("Connected to server...")
            server.login(smtp_username, smtp_password)
            print("Logged in successfully...")
            server.send_message(message)
            print(f"Test email sent successfully to {recipient_email}")
        return True
    
    except Exception as e:
        print(f"Failed to send test email: {str(e)}")
        return False

import smtplib
import ssl
import getpass

def test_simple_email():
    sender = "newsletter@efels.com"
    recipient = input("Enter recipient email: ")
    password = getpass.getpass("Enter password: ")
    
    message = f"""\
Subject: Simple Test Email

This is a test email from {sender} to verify the email configuration works.
"""
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("mail.efels.com", 465, context=context) as server:
            print("Connecting to server...")
            server.login(sender, password)
            print("Logged in successfully")
            server.sendmail(sender, recipient, message)
            print("Email sent successfully")
    except Exception as e:
        print(f"Error: {e}")

import smtplib
import getpass
from email.mime.text import MIMEText

def test_email_tls():
    sender = "newsletter@efels.com"
    recipient = input("Enter recipient email: ")
    password = getpass.getpass("Enter password: ")
    
    msg = MIMEText("This is a test email sent using TLS on port 587.")
    msg['Subject'] = 'Test Email (TLS)'
    msg['From'] = sender
    msg['To'] = recipient
    
    try:
        server = smtplib.SMTP('mail.efels.com', 587)
        print("Connected to server")
        server.starttls()  # Upgrade to secure connection
        print("TLS connection established")
        server.login(sender, password)
        print("Login successful")
        server.send_message(msg)
        print("Email sent successfully")
        server.quit()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_email_tls()