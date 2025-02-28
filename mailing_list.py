import secrets
from datetime import datetime, timezone
import logging
from fasthtml.common import *
from monsterui.all import *
from fastlite import *
import sys

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

def send_verification_email(recipient_email, confirmation_token, base_url):
    """
    Send a verification email to a new subscriber
    
    Args:
        recipient_email (str): The email address of the recipient
        confirmation_token (str): The token to verify the email
        base_url (str): The base URL of your website
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Email configuration - consider moving these to environment variables
    sender_email = os.environ.get('EMAIL_SENDER', 'your-email@example.com')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME', sender_email)
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    
    # Create verification URL
    verification_url = f"{base_url}/confirm-email/{confirmation_token}"
    
    # Create email
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'Please confirm your subscription'
    
    # Email body
    body = f"""
    <html>
    <body>
        <h2>Thank you for subscribing!</h2>
        <p>Please click the link below to confirm your subscription:</p>
        <p><a href="{verification_url}">Confirm my subscription</a></p>
        <p>If you didn't subscribe to our newsletter, please ignore this email.</p>
    </body>
    </html>
    """
    
    message.attach(MIMEText(body, 'html'))
    
    try:
        # Connect to server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_username, smtp_password)
        
        # Send email
        server.send_message(message)
        server.quit()
        
        logger.info(f"Verification email sent to {recipient_email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        return False

# Logging setup
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database connection - use a function to avoid circular imports
def get_db():
    return database("subscribers.sqlite")

# Create table if it doesn't exist
def initialize_subscribers_table():
    db = get_db()
    if 'subscribers' not in db.t:
        db.t.subscribers.create(
            id=int,
            email=str,
            signup_date=str,
            confirmed=bool,
            confirmation_token=str,
            pk='id'
        )
    return db

# UI Components
def mailing_list_signup():
    return Div(
        H3("Subscribe to my Newsletter", cls="text-lg font-bold mb-2 text-primary"),
        P("Get the latest updates directly to your inbox", 
          cls="text-sm text-muted-foreground mb-3"),
        Input(
            type="email", 
            id="email-input",
            name="email",
            placeholder="Your email address", 
            required=True,
            cls="w-full p-2 border border-primary/30 rounded-md mb-2"
        ),
        Button(
            "Subscribe",
            hx_get="/subscribe",
            hx_include="#email-input",
            hx_target="closest div",
            hx_swap="innerHTML",
            cls="w-full bg-primary text-primary-foreground hover:bg-primary/80 p-2 rounded-md"
        ),
        cls="bg-card p-4 rounded-lg shadow-sm border border-primary/20 mb-4"
    )

# Route handlers
async def handle_subscription(request, email: str = ''):
    logger.debug(f"=== SUBSCRIBE ENDPOINT CALLED with email: {email} ===")
    
    try:
        if not email:
            return Div(P("Email address is required", cls="text-red-600"))
        
        # Generate confirmation token
        confirmation_token = secrets.token_urlsafe(32)
        
        # Save to database
        db = get_db()
        db.execute(
            'INSERT INTO subscribers (email, signup_date, confirmed, confirmation_token) VALUES (?, ?, ?, ?)',
            [email, datetime.now(timezone.utc).isoformat(), False, confirmation_token]
        )
        logger.debug(f"Saved email: {email}")
        
        # Get the base URL from the request
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        
        # Send verification email
        email_sent = send_verification_email(email, confirmation_token, base_url)
        
        if email_sent:
            return Div(
                H3("Thank you for subscribing!", cls="text-lg font-bold text-primary"),
                P("Please check your email to confirm your subscription.", 
                  cls="text-sm text-muted-foreground"),
                cls="p-4 text-center"
            )
        else:
            # Email failed to send but user was added to database
            return Div(
                H3("Thank you for subscribing!", cls="text-lg font-bold text-primary"),
                P("There was an issue sending your confirmation email. Please try again later.", 
                  cls="text-sm text-muted-foreground"),
                cls="p-4 text-center"
            )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Div(P(f"Something went wrong: {str(e)}", cls="text-red-600"))

async def confirm_email(request, token: str):
    try:
        db = get_db()
        # Find subscriber with this token
        subscriber = db.execute(
            'SELECT * FROM subscribers WHERE confirmation_token = ? AND confirmed = 0',
            [token]
        ).fetchone()
        
        if not subscriber:
            return Div(
                H3("Invalid confirmation link", cls="text-lg font-bold text-red-600"),
                P("This confirmation link is invalid or has already been used.", 
                  cls="text-sm text-muted-foreground"),
                cls="p-4 text-center"
            )
        
        # Update subscriber as confirmed
        db.execute(
            'UPDATE subscribers SET confirmed = 1 WHERE confirmation_token = ?',
            [token]
        )
        
        return Div(
            H3("Subscription confirmed!", cls="text-lg font-bold text-primary"),
            P("Thank you for confirming your email address. You're now subscribed to our newsletter!", 
              cls="text-sm text-muted-foreground"),
            cls="p-4 text-center"
        )
    
    except Exception as e:
        logger.error(f"Error confirming email: {str(e)}")
        return Div(P(f"Something went wrong: {str(e)}", cls="text-red-600"))

async def view_subscribers(request):
    try:
        db = get_db()
        subscribers_list = db.execute('SELECT * FROM subscribers ORDER BY id DESC LIMIT 10').fetchall()
        return Div(
            H3("Recent Subscribers", cls="text-lg font-bold mb-4"),
            *[Div(
                P(f"Email: {sub[1]}", cls="font-medium"),
                P(f"Signed up: {sub[2]}", cls="text-sm text-muted-foreground"),
                P(f"Confirmed: {'Yes' if sub[3] else 'No'}", cls="text-sm"),
                cls="p-4 border rounded-lg mb-2"
            ) for sub in subscribers_list],
            cls="p-4"
        )
    except Exception as e:
        return Div(P(f"Error: {str(e)}", cls="text-red-600"))

# Test routes (you might want to remove these in production)
async def test_db(request):
    try:
        db = get_db()
        table_info = db.execute('PRAGMA table_info(subscribers)').fetchall()
        count = db.execute('SELECT COUNT(*) FROM subscribers').fetchone()
        return {
            'table_structure': table_info,
            'row_count': count[0] if count else 0
        }
    except Exception as e:
        return {'error': str(e)}

async def test_add_email(email: str, request):
    try:
        db = get_db()
        new_sub = {
            'email': email,
            'signup_date': datetime.now(timezone.utc).isoformat(),
            'confirmed': False,
            'confirmation_token': 'test123'
        }
        
        # Try direct SQL insert
        db.execute(
            'INSERT INTO subscribers (email, signup_date, confirmed, confirmation_token) VALUES (?, ?, ?, ?)',
            [email, new_sub['signup_date'], False, 'test123']
        )
        
        return {
            'status': 'success',
            'email': email,
            'current_data': db.execute('SELECT * FROM subscribers').fetchall()
        }
    except Exception as e:
        return {'error': str(e)}

async def test_insert(request):
    try:
        db = get_db()
        test_data = {
            'email': 'test@example.com',
            'signup_date': datetime.now(timezone.utc).isoformat(),
            'confirmed': False,
            'confirmation_token': 'test_token'
        }
        
        logger.debug("Attempting test insert...")
        result = db.t.subscribers.insert(test_data)
        logger.debug(f"Insert result: {result}")
        
        # Check if it was saved
        count = db.execute('SELECT COUNT(*) FROM subscribers').fetchone()
        data = db.execute('SELECT * FROM subscribers').fetchall()
        
        return {
            'insert_result': result,
            'count': count[0],
            'all_data': data
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {'error': str(e)}