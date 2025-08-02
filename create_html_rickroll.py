import random
import urllib.parse

def create_html_rickroll_email(sender_name, spam_subject, rickroll_url):
    """
    Create clean, professional security alert email that hides rickroll link
    """
    
    # Generate verification parameters
    session_id = f"SEC{random.randint(100000, 999999)}"
    verification_token = f"VT{random.randint(1000000, 9999999)}"
    
    # Create fake verification URL
    fake_url = f"https://account-security-center.com/verify?session={session_id}&token={verification_token}"
    
    # Clean, professional HTML template matching your original image
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>SECURITY ALERT</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                line-height: 1.5; 
                color: #333; 
                background-color: #f8f9fa; 
                margin: 0; 
                padding: 20px;
            }}
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background-color: white; 
                border-radius: 8px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{ 
                background-color: #dc3545; 
                color: white; 
                padding: 20px; 
                text-align: center; 
            }}
            .header h1 {{ 
                margin: 0; 
                font-size: 24px; 
                font-weight: 600;
            }}
            .content {{ 
                padding: 30px; 
            }}
            .alert-box {{ 
                background-color: #fff3cd; 
                border-left: 4px solid #ffc107; 
                padding: 15px; 
                margin: 20px 0; 
            }}
            .verify-btn {{ 
                display: inline-block;
                background-color: #dc3545; 
                color: white; 
                padding: 12px 30px; 
                text-decoration: none; 
                border-radius: 6px; 
                font-weight: 600;
                text-align: center;
                margin: 25px 0;
            }}
            .verify-btn:hover {{ 
                background-color: #c82333; 
            }}
            .consequences {{ 
                background-color: #f8f9fa; 
                padding: 20px; 
                border-radius: 6px; 
                margin: 20px 0; 
            }}
            .consequences ul {{ 
                margin: 10px 0; 
                padding-left: 20px; 
            }}
            .consequences li {{ 
                margin: 5px 0; 
            }}
            .footer {{ 
                background-color: #6c757d; 
                color: white; 
                padding: 20px; 
                text-align: center; 
                font-size: 12px; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚠️ SECURITY ALERT ⚠️</h1>
                <p style="margin: 5px 0 0 0;">Immediate Action Required</p>
            </div>
            
            <div class="content">
                <p>Dear <strong>"{sender_name}"</strong>,</p>
                
                <p>We have detected suspicious spam activity from your account!</p>
                
                <div class="alert-box">
                    <strong>Your recent email with subject "{spam_subject}" has been flagged by our advanced AI spam detection system.</strong>
                </div>
                
                <p><strong>⚡ IMMEDIATE ACTION REQUIRED</strong></p>
                
                <p>To prevent your account from being permanently suspended, you must verify your identity within 24 hours.</p>
                
                <div style="text-align: center;">
                    <a href="{rickroll_url}" class="verify-btn">
                        🔐 VERIFY ACCOUNT NOW
                    </a>
                </div>
                
                <div class="consequences">
                    <strong>What happens if you don't verify:</strong>
                    <ul>
                        <li>Your email account will be flagged</li>
                        <li>All future emails will be blocked</li>
                        <li>Your IP address will be reported to authorities</li>
                        <li>Your internet provider will be notified</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>Anti-Spam Defense System<br>
                Automated Security Response</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_template = f"""
⚠️ SECURITY ALERT ⚠️

Dear "{sender_name}",

We have detected suspicious spam activity from your account!

Your recent email with subject "{spam_subject}" has been flagged by our advanced AI spam detection system.

⚡ IMMEDIATE ACTION REQUIRED

To prevent your account from being permanently suspended, you must verify your identity within 24 hours.

VERIFY YOUR ACCOUNT NOW: {fake_url}

What happens if you don't verify:
• Your email account will be flagged
• All future emails will be blocked
• Your IP address will be reported to authorities
• Your internet provider will be notified

---
Anti-Spam Defense System
Automated Security Response
    """
    
    return {
        'html': html_template,
        'text': text_template,
        'subject': "⚠️ SECURITY ALERT ⚠️",
        'fake_url': fake_url
    }
