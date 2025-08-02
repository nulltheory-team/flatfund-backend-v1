from fastapi import APIRouter, Depends, HTTPException, status, Response, Header
from typing import Optional
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import random
import string
import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from ..database import get_db
import secrets
from ..models import Apartment, User, OTPVerification, UserRole, FlatmateInvitation, RefreshToken, Security
from ..schemas import (
    SendOTPRequest, VerifyOTPRequest, AuthResponse, AssignTenantRequest, AssignTenantResponse,
    InviteFlatmateRequest, InviteFlatmateResponse, FlatmateSignupRequest, FlatmateSignupResponse,
    SelectApartmentRequest, SelectApartmentResponse, LoginRequest, LoginResponse, RefreshTokenRequest, TokenResponse,
    UpdateFlatmateDetailsRequest, UpdateFlatmateDetailsResponse, GetFlatmateDetailsResponse, SuggestedFlatDetails
)

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/v1", tags=["authentication"])

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 days
REFRESH_TOKEN_EXPIRE_DAYS = 60  # Long-lived refresh token

# Brevo Configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

def generate_otp() -> str:
    """Generate a 4-digit OTP"""
    return ''.join(random.choices(string.digits, k=4))

def generate_invitation_code() -> str:
    """Generate a 6-character alphanumeric invitation code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=6))

def send_otp_email(email: str, otp: str, apartment_name: str):
    """Send OTP via Brevo email service"""
    if not BREVO_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Email service not configured. Please set BREVO_API_KEY environment variable."
        )
    
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    subject = f"🔐 Your FlatFund Access Code for {apartment_name}"
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FlatFund OTP Verification</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                padding: 40px 30px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: float 6s ease-in-out infinite;
            }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
                50% {{ transform: translateY(-20px) rotate(180deg); }}
            }}
            
            .logo {{
                font-size: 32px;
                font-weight: 700;
                color: white;
                margin-bottom: 10px;
                position: relative;
                z-index: 2;
            }}
            
            .header-subtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: 500;
                position: relative;
                z-index: 2;
            }}
            
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            
            .greeting {{
                font-size: 24px;
                font-weight: 600;
                color: #1F2937;
                margin-bottom: 16px;
            }}
            
            .message {{
                font-size: 16px;
                color: #6B7280;
                margin-bottom: 32px;
                line-height: 1.7;
            }}
            
            .apartment-info {{
                background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 32px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }}
            
            .apartment-name {{
                font-size: 18px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 4px;
            }}
            
            .otp-container {{
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                border-radius: 20px;
                padding: 32px;
                margin: 32px 0;
                position: relative;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
            }}
            
            .otp-container::before {{
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #4F46E5, #7C3AED, #EC4899, #EF4444, #F59E0B, #10B981, #06B6D4);
                border-radius: 22px;
                z-index: -1;
                animation: gradient 3s ease infinite;
                background-size: 400% 400%;
            }}
            
            @keyframes gradient {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            .otp-label {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
            }}
            
            .otp-code {{
                font-size: 48px;
                font-weight: 700;
                color: white;
                letter-spacing: 8px;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                font-family: 'Monaco', 'Menlo', monospace;
            }}
            
            .timer-info {{
                background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
                border-radius: 12px;
                padding: 16px 20px;
                margin: 24px 0;
                border-left: 4px solid #F59E0B;
            }}
            
            .timer-icon {{
                font-size: 20px;
                margin-right: 8px;
            }}
            
            .timer-text {{
                color: #92400E;
                font-weight: 500;
                font-size: 14px;
            }}
            
            .security-note {{
                background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
                border-radius: 12px;
                padding: 20px;
                margin: 24px 0;
                border-left: 4px solid #3B82F6;
            }}
            
            .security-text {{
                color: #1E40AF;
                font-size: 14px;
                line-height: 1.6;
            }}
            
            .footer {{
                background: #F9FAFB;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #E5E7EB;
            }}
            
            .footer-text {{
                color: #6B7280;
                font-size: 14px;
                margin-bottom: 16px;
            }}
            
            .company-info {{
                color: #9CA3AF;
                font-size: 12px;
            }}
            
            .divider {{
                height: 1px;
                background: linear-gradient(90deg, transparent 0%, #E5E7EB 50%, transparent 100%);
                margin: 24px 0;
            }}
            
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 20px;
                }}
                
                .content {{
                    padding: 30px 20px;
                }}
                
                .otp-code {{
                    font-size: 36px;
                    letter-spacing: 4px;
                }}
                
                .header {{
                    padding: 30px 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">🏢 FlatFund</div>
                <div class="header-subtitle">Secure Apartment Management</div>
            </div>
            
            <div class="content">
                <div class="greeting">Hello! 👋</div>
                
                <div class="message">
                    You've requested access to your apartment management dashboard. 
                    Please use the verification code below to complete your sign-in.
                </div>
                
                <div class="apartment-info">
                    <div class="apartment-name">🏠 {apartment_name}</div>
                    <div style="color: #6B7280; font-size: 14px;">Your apartment management portal</div>
                </div>
                
                <div class="otp-container">
                    <div class="otp-label">Your Verification Code</div>
                    <div class="otp-code">{otp}</div>
                </div>
                
                <div class="timer-info">
                    <span class="timer-icon">⏰</span>
                    <span class="timer-text">This code expires in 10 minutes</span>
                </div>
                
                <div class="divider"></div>
                
                <div class="security-note">
                    <div class="security-text">
                        <strong>🔒 Security Note:</strong><br>
                        Never share this code with anyone. FlatFund staff will never ask for your verification code.
                        If you didn't request this code, please ignore this email.
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-text">
                    Best regards,<br>
                    <strong>The FlatFund Team</strong>
                </div>
                
                <div class="company-info">
                    This email was sent from a secure FlatFund server.<br>
                    © 2025 FlatFund. All rights reserved.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    sender = {"name": "FlatFund Team", "email": "team.nulltheory@gmail.com"}
    to = [{"email": email}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        sender=sender,
        subject=subject
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"Exception when calling SMTPApi->send_transac_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP email")

def send_flatmate_invitation_email(email: str, apartment_name: str, flat_number: str, flat_floor: str, invitation_code: str):
    """Send flatmate invitation email with 6-character code"""
    if not BREVO_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Email service not configured. Please set BREVO_API_KEY environment variable."
        )
    
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    subject = f"🏠 You're Invited to Join {apartment_name} on FlatFund!"
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FlatFund Invitation</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                padding: 40px 30px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: float 6s ease-in-out infinite;
            }}
            
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
                50% {{ transform: translateY(-20px) rotate(180deg); }}
            }}
            
            .logo {{
                font-size: 32px;
                font-weight: 700;
                color: white;
                margin-bottom: 10px;
                position: relative;
                z-index: 2;
            }}
            
            .header-subtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: 500;
                position: relative;
                z-index: 2;
            }}
            
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            
            .greeting {{
                font-size: 24px;
                font-weight: 600;
                color: #1F2937;
                margin-bottom: 16px;
            }}
            
            .message {{
                font-size: 16px;
                color: #6B7280;
                margin-bottom: 32px;
                line-height: 1.7;
            }}
            
            .apartment-info {{
                background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 32px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }}
            
            .apartment-name {{
                font-size: 20px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 8px;
            }}
            
            .flat-info {{
                font-size: 16px;
                color: #6B7280;
                font-weight: 500;
            }}
            
            .code-container {{
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                border-radius: 20px;
                padding: 32px;
                margin: 32px 0;
                position: relative;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
            }}
            
            .code-container::before {{
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #4F46E5, #7C3AED, #EC4899, #EF4444, #F59E0B, #10B981, #06B6D4);
                border-radius: 22px;
                z-index: -1;
                animation: gradient 3s ease infinite;
                background-size: 400% 400%;
            }}
            
            @keyframes gradient {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            .code-label {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
            }}
            
            .invitation-code {{
                font-size: 36px;
                font-weight: 700;
                color: white;
                letter-spacing: 4px;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                font-family: 'Monaco', 'Menlo', monospace;
            }}
            
            .instructions {{
                background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
                border-radius: 12px;
                padding: 20px;
                margin: 24px 0;
                border-left: 4px solid #F59E0B;
            }}
            
            .instructions-text {{
                color: #92400E;
                font-size: 14px;
                line-height: 1.6;
            }}
            
            .footer {{
                background: #F9FAFB;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #E5E7EB;
            }}
            
            .footer-text {{
                color: #6B7280;
                font-size: 14px;
                margin-bottom: 16px;
            }}
            
            .company-info {{
                color: #9CA3AF;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">🏢 FlatFund</div>
                <div class="header-subtitle">You're Invited!</div>
            </div>
            
            <div class="content">
                <div class="greeting">Welcome to the Community! 🎉</div>
                
                <div class="message">
                    You have been invited to join the apartment management system for your new home.
                    Use the code below to complete your registration and start managing your apartment.
                </div>
                
                <div class="apartment-info">
                    <div class="apartment-name">🏠 {apartment_name}</div>
                    <div class="flat-info">📍 Flat Number: {flat_number} (Floor: {flat_floor})</div>
                </div>
                
                <div class="code-container">
                    <div class="code-label">Your Invitation Code</div>
                    <div class="invitation-code">{invitation_code}</div>
                </div>
                
                <div class="instructions">
                    <div class="instructions-text">
                        <strong>📋 Next Steps:</strong><br>
                        1. Visit the FlatFund signup page<br>
                        2. Enter your email address (this one)<br>
                        3. Enter the invitation code above<br>
                        4. Complete your registration<br>
                        5. Login to access your apartment dashboard
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-text">
                    Welcome to your new home management system!<br>
                    <strong>The FlatFund Team</strong>
                </div>
                
                <div class="company-info">
                    This invitation expires in 7 days. If you need help, contact your apartment admin.<br>
                    © 2025 FlatFund. All rights reserved.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    sender = {"name": "FlatFund Team", "email": "team.nulltheory@gmail.com"}
    to = [{"email": email}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        sender=sender,
        subject=subject
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"Exception when calling SMTPApi->send_transac_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send invitation email")

def send_login_otp_email(email: str, otp: str, apartment_name: str, flat_number: str, flat_floor: str, role: str):
    """Send login OTP email to user"""
    if not BREVO_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Email service not configured. Please set BREVO_API_KEY environment variable."
        )
    
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    subject = f"🔐 Your FlatFund Login Code for {apartment_name}"
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FlatFund Login OTP</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                padding: 40px 30px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .logo {{
                font-size: 32px;
                font-weight: 700;
                color: white;
                margin-bottom: 10px;
            }}
            
            .header-subtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: 500;
            }}
            
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            
            .greeting {{
                font-size: 24px;
                font-weight: 600;
                color: #1F2937;
                margin-bottom: 16px;
            }}
            
            .user-info {{
                background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 32px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }}
            
            .apartment-name {{
                font-size: 20px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 8px;
            }}
            
            .user-details {{
                font-size: 14px;
                color: #6B7280;
            }}
            
            .otp-container {{
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                border-radius: 20px;
                padding: 32px;
                margin: 32px 0;
                position: relative;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
            }}
            
            .otp-label {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
            }}
            
            .otp-code {{
                font-size: 48px;
                font-weight: 700;
                color: white;
                letter-spacing: 8px;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                font-family: 'Monaco', 'Menlo', monospace;
            }}
            
            .timer-info {{
                background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
                border-radius: 12px;
                padding: 16px 20px;
                margin: 24px 0;
                border-left: 4px solid #F59E0B;
            }}
            
            .timer-text {{
                color: #92400E;
                font-weight: 500;
                font-size: 14px;
            }}
            
            .footer {{
                background: #F9FAFB;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #E5E7EB;
            }}
            
            .footer-text {{
                color: #6B7280;
                font-size: 14px;
                margin-bottom: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">🏢 FlatFund</div>
                <div class="header-subtitle">Secure Login</div>
            </div>
            
            <div class="content">
                <div class="greeting">Welcome back! 👋</div>
                
                <div class="user-info">
                    <div class="apartment-name">🏠 {apartment_name}</div>
                    <div class="user-details">
                        📍 Flat: {flat_number} (Floor: {flat_floor}) | 👤 Role: {role.title()}
                    </div>
                </div>
                
                <div class="otp-container">
                    <div class="otp-label">Your Login Code</div>
                    <div class="otp-code">{otp}</div>
                </div>
                
                <div class="timer-info">
                    <span class="timer-text">⏰ This code expires in 10 minutes</span>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-text">
                    <strong>The FlatFund Team</strong>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    sender = {"name": "FlatFund Team", "email": "team.nulltheory@gmail.com"}
    to = [{"email": email}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        sender=sender,
        subject=subject
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"Exception when calling SMTPApi->send_transac_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send login OTP email")

def send_welcome_email(email: str, apartment_name: str, flat_number: str, flat_floor: str, role: str):
    """Send welcome email after successful registration"""
    if not BREVO_API_KEY:
        print("Email service not configured - skipping welcome email")
        return
    
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    subject = f"🎉 Welcome to {apartment_name} - Registration Successful!"
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to FlatFund</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                padding: 40px 30px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .logo {{
                font-size: 32px;
                font-weight: 700;
                color: white;
                margin-bottom: 10px;
            }}
            
            .header-subtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: 500;
            }}
            
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            
            .greeting {{
                font-size: 24px;
                font-weight: 600;
                color: #1F2937;
                margin-bottom: 16px;
            }}
            
            .message {{
                font-size: 16px;
                color: #6B7280;
                margin-bottom: 32px;
                line-height: 1.7;
            }}
            
            .registration-info {{
                background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 32px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }}
            
            .apartment-name {{
                font-size: 20px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 8px;
            }}
            
            .details {{
                font-size: 14px;
                color: #6B7280;
                margin: 4px 0;
            }}
            
            .role-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 8px;
            }}
            
            .next-steps {{
                background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
                border-radius: 12px;
                padding: 20px;
                margin: 24px 0;
                border-left: 4px solid #3B82F6;
            }}
            
            .next-steps-text {{
                color: #1E40AF;
                font-size: 14px;
                line-height: 1.6;
                text-align: left;
            }}
            
            .footer {{
                background: #F9FAFB;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #E5E7EB;
            }}
            
            .footer-text {{
                color: #6B7280;
                font-size: 14px;
                margin-bottom: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">🏢 FlatFund</div>
                <div class="header-subtitle">Registration Successful!</div>
            </div>
            
            <div class="content">
                <div class="greeting">Welcome to your new home! 🎉</div>
                
                <div class="message">
                    Congratulations! Your registration has been completed successfully. 
                    You are now part of the apartment management system.
                </div>
                
                <div class="registration-info">
                    <div class="apartment-name">🏠 {apartment_name}</div>
                    <div class="details">📍 <strong>Flat:</strong> {flat_number} (Floor: {flat_floor})</div>
                    <div class="details">📧 <strong>Email:</strong> {email}</div>
                    <div class="role-badge">{role.title()}</div>
                </div>
                
                <div class="next-steps">
                    <div class="next-steps-text">
                        <strong>🚀 What's Next?</strong><br>
                        1. <strong>Login:</strong> Use the login page to access your dashboard<br>
                        2. <strong>Select Apartment:</strong> Choose your apartment from the list<br>
                        3. <strong>OTP Verification:</strong> You'll receive a login code via email<br>
                        4. <strong>Complete Profile:</strong> Add your personal details and preferences<br>
                        5. <strong>Start Managing:</strong> Track expenses, communicate with neighbors, and more!
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-text">
                    Welcome to the community!<br>
                    <strong>The FlatFund Team</strong>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    sender = {"name": "FlatFund Team", "email": "team.nulltheory@gmail.com"}
    to = [{"email": email}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        sender=sender,
        subject=subject
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"Exception when calling SMTPApi->send_transac_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send welcome email")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(db: Session, user_id: int) -> str:
    """Generate a secure opaque refresh token, store it, and return it."""
    # Invalidate all old refresh tokens for this user for better security
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).update({"is_revoked": 1})

    # Generate a new secure random token
    token = secrets.token_hex(32)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)
    
    return token

@router.post("/signin")
async def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """Send OTP to admin email for apartment signin"""
    
    # Verify apartment exists
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == request.apt_id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found"
        )
    
    # Check if email exists in apartment (either as admin or any valid user)
    # For now, we allow both admin_email and other emails to request OTP
    # The role will be determined during verification
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 minutes expiry
    
    # Delete any existing OTP for this email/apartment combination
    db.query(OTPVerification).filter(
        OTPVerification.email == request.admin_email,
        OTPVerification.apartment_id == request.apt_id
    ).delete()
    
    # Create new OTP record
    otp_record = OTPVerification(
        email=request.admin_email,
        apartment_id=request.apt_id,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp_record)
    db.commit()
    
    # Send OTP via email
    try:
        send_otp_email(request.admin_email, otp_code, apartment.apartment_name)
    except Exception as e:
        # Rollback OTP record if email fails
        db.delete(otp_record)
        db.commit()
        raise e
    
    return {
        "status": True,
        "message": "OTP sent successfully to your email",
        "expires_in_minutes": 10
    }

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP and return authentication token"""
    
    # Get apartment details
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == request.apt_id
    ).first()
    
    if not apartment:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": False, "message": "Apartment not found"}
        )
    
    # Verify OTP
    otp_record = db.query(OTPVerification).filter(
        OTPVerification.email == request.admin_email,
        OTPVerification.apartment_id == request.apt_id,
        OTPVerification.otp_code == request.otp,
        OTPVerification.is_verified == 0,
        OTPVerification.expires_at > datetime.utcnow()
    ).first()
    
    if not otp_record:
        # Check for specific reasons for failure for better client-side feedback
        existing_otp = db.query(OTPVerification).filter(
            OTPVerification.email == request.admin_email,
            OTPVerification.apartment_id == request.apt_id,
            OTPVerification.otp_code == request.otp
        ).first()

        if existing_otp and existing_otp.is_verified:
            message = "OTP has already been used."
        elif existing_otp and existing_otp.expires_at <= datetime.utcnow():
            message = "OTP has expired. Please request a new one."
        else:
            message = "Invalid OTP. Please check the code and try again."

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": False, "message": message}
        )
    
    # Mark OTP as verified
    otp_record.is_verified = 1
    db.commit()
    
    # Determine user role based on email comparison
    if request.admin_email.lower() == apartment.admin_email.lower():
        user_role = UserRole.ADMIN
        flat_id_prefix = "admin"
    else:
        # For non-admin emails, assign OWNER role
        # TENANT role will only be assigned through invitation
        user_role = UserRole.OWNER
        flat_id_prefix = "owner"
    
    # Check if user exists, if not create one
    user = db.query(User).filter(
        User.user_email_id == request.admin_email,
        User.apartment_id == request.apt_id
    ).first()
    
    if not user:
        # Create new user with appropriate role
        user = User(
            flat_id=f"{flat_id_prefix}_{apartment.apartment_id}",
            apartment_uuid=apartment.apartment_uuid,
            apartment_id=apartment.apartment_id,
            user_email_id=request.admin_email,
            role=user_role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # For existing users, only update role if they are changing from/to admin  
        # Keep existing OWNER/TENANT roles as they are (don't override)
        if (user.role == UserRole.ADMIN and user_role != UserRole.ADMIN) or \
           (user.role != UserRole.ADMIN and user_role == UserRole.ADMIN):
            user.role = user_role
            user.flat_id = f"{flat_id_prefix}_{apartment.apartment_id}"
            db.commit()
            db.refresh(user)
    
    # Create JWT token
    token_data = {
        "sub": user.flat_id, # Use flat_id as subject for privacy
        "user_id": str(user.id),
        "apt_id": apartment.apartment_id,
        "apt_uuid": str(apartment.apartment_uuid),
        "role": user.role.value
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(db=db, user_id=user.id)
    
    # Check if user details are filled
    is_all_user_details_filled = bool(
        user.user_name and 
        user.user_phone_number and 
        user.flat_number is not None and 
        user.flat_floor is not None
    )
    
    # Check if there's an invitation for this user that could provide flat details
    suggested_flat_details = None
    if not is_all_user_details_filled:
        # Look for any invitation (used or unused) for this user to get flat suggestions
        invitation = db.query(FlatmateInvitation).filter(
            FlatmateInvitation.apartment_id == request.apt_id,
            FlatmateInvitation.invited_email == request.admin_email
        ).order_by(FlatmateInvitation.created_at.desc()).first()
        
        if invitation:
            suggested_flat_details = {
                "flat_number": invitation.flat_number,
                "flat_floor": invitation.floor
            }
    
    response_data = {
        "apt_id": apartment.apartment_id,
        "apt_uuid": str(apartment.apartment_uuid),
        "flat_id": user.flat_id,
        "flat_uuid": str(user.flat_uuid),
        "user_id": f"user_{user.id}",
        "is_all_user_details_filled": is_all_user_details_filled,
        "role": user.role.value,
        "suggested_flat_details": suggested_flat_details  # 🆕 NEW FIELD
    }
    
    return AuthResponse(
        status=True,
        message="OTP verified successfully",
        token=TokenResponse(access_token=access_token, refresh_token=refresh_token),
        data=response_data
    )

@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh the access token using a secure, opaque refresh token.
    Implements token rotation for enhanced security.
    """
    token = request.refresh_token
    
    # Find the refresh token in the database
    db_refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.is_revoked == 0,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()

    if not db_refresh_token:
        # This could be a sign of a compromised token being reused.
        # For extra security, you could log this event.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- Token Rotation ---
    # Invalidate the used refresh token
    db_refresh_token.is_revoked = 1
    db.commit()

    user = db_refresh_token.user
    if not user:
        # This case should be rare due to database foreign key constraints
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found for the given token",
        )

    # Issue a new access token
    token_data = {
        "sub": user.flat_id,
        "user_id": str(user.id),
        "apt_id": user.apartment_id,
        "apt_uuid": str(user.apartment_uuid),
        "role": user.role.value,
    }
    new_access_token = create_access_token(data=token_data)
    
    # Issue a new refresh token
    new_refresh_token = create_refresh_token(db=db, user_id=user.id)

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)

@router.put("/user/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db)
):
    """Update user role (admin can change owner <-> tenant, only admin email can be admin)"""
    
    # Validate role
    try:
        role_enum = UserRole(new_role.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {[role.value for role in UserRole]}"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Get apartment to check admin email
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == user.apartment_id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found"
        )
    
    # Security check: Only allow admin role for admin email
    if role_enum == UserRole.ADMIN and user.user_email_id.lower() != apartment.admin_email.lower():
        raise HTTPException(
            status_code=403,
            detail="Admin role can only be assigned to the apartment admin email"
        )
    
    # Prevent removing admin role from admin email (they must remain admin)
    if user.user_email_id.lower() == apartment.admin_email.lower() and role_enum != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Cannot change role for apartment admin email - must remain admin"
        )
    
    # Update user role
    old_role = user.role.value
    user.role = role_enum
    
    # Update flat_id prefix
    if role_enum == UserRole.ADMIN:
        user.flat_id = f"admin_{apartment.apartment_id}"
    elif role_enum == UserRole.OWNER:
        user.flat_id = f"owner_{apartment.apartment_id}"
    else:  # TENANT
        user.flat_id = f"tenant_{apartment.apartment_id}"
    
    db.commit()
    db.refresh(user)
    
    return {
        "status": True,
        "message": f"User role updated from {old_role} to {role_enum.value}",
        "user": {
            "user_id": user.id,
            "email": user.user_email_id,
            "old_role": old_role,
            "new_role": role_enum.value,
            "flat_id": user.flat_id
        }
    }

@router.post("/invite-flatmate", response_model=InviteFlatmateResponse, 
            summary="Invite Flatmate with Floor Information",
            description="""
            Invite a new flatmate to join an apartment with comprehensive floor information.
            
            **Features:**
            - Sends beautiful HTML invitation email with 6-character secure code
            - Supports Indian apartment floor conventions (B, G, 1, 2, etc.)
            - Floor information is captured and will be inherited by the new user
            - 7-day invitation expiry
            
            **Indian Floor Conventions Supported:**
            - "B" - Basement
            - "G" - Ground Floor
            - "1", "2", "3"... - Numbered floors  
            - "M" - Mezzanine
            - "UG" - Upper Ground
            
            **Email Features:**
            - Professional glassmorphism design
            - Floor context: "Flat 101 (Floor: G)"
            - Step-by-step signup instructions
            - Secure invitation code display
            """,
            tags=["Authentication", "Invitations"])
async def invite_flatmate(request: InviteFlatmateRequest, db: Session = Depends(get_db)):
    """Admin invites a flatmate by providing apt_id, flat_number, and owner_email_id"""
    
    # Verify apartment exists
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == request.apt_id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found"
        )
    
    # Check if there's already an active invitation for this email + apartment + flat
    existing_invitation = db.query(FlatmateInvitation).filter(
        FlatmateInvitation.apartment_id == request.apt_id,
        FlatmateInvitation.flat_number == request.flat_number,
        FlatmateInvitation.invited_email == request.owner_email_id,
        FlatmateInvitation.is_used == 0,
        FlatmateInvitation.expires_at > datetime.utcnow()
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=400,
            detail="Active invitation already exists for this email and flat. Please wait for it to expire or be used."
        )
    
    # Generate unique 6-character invitation code
    invitation_code = generate_invitation_code()
    
    # Ensure code is unique
    while db.query(FlatmateInvitation).filter(FlatmateInvitation.invitation_code == invitation_code).first():
        invitation_code = generate_invitation_code()
    
    # Create invitation record
    expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
    
    invitation = FlatmateInvitation(
        apartment_id=request.apt_id,
        flat_number=request.flat_number,
        floor=request.floor,
        invited_email=request.owner_email_id,
        invitation_code=invitation_code,
        invited_by_admin_email=apartment.admin_email,
        expires_at=expires_at
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # Send invitation email
    try:
        send_flatmate_invitation_email(
            request.owner_email_id, 
            apartment.apartment_name, 
            request.flat_number,
            request.floor,  # Include floor from request
            invitation_code
        )
    except Exception as e:
        # Rollback invitation if email fails
        db.delete(invitation)
        db.commit()
        raise e
    
    response_data = {
        "invitation_id": str(invitation.invitation_uuid),
        "apartment_id": apartment.apartment_id,
        "apartment_name": apartment.apartment_name,
        "flat_number": request.flat_number,
        "floor": request.floor,
        "invited_email": request.owner_email_id,
        "invitation_code": invitation_code,
        "expires_at": expires_at.isoformat(),
        "expires_in_days": 7
    }
    
    return InviteFlatmateResponse(
        status=True,
        message="Flatmate invitation sent successfully",
        data=response_data
    )

@router.post("/signup", response_model=FlatmateSignupResponse,
            summary="Flatmate Signup with Floor Inheritance", 
            description="""
            Complete flatmate registration using invitation code with automatic floor inheritance.
            
            **Features:**
            - Secure 6-character invitation code verification
            - Automatic floor inheritance from invitation (no manual floor entry needed)
            - Role-based assignment (OWNER for first user, TENANT for subsequent users)
            - Professional welcome email with floor information
            - JWT token generation for immediate access
            
            **Floor Inheritance Process:**
            1. System validates invitation code
            2. Retrieves floor information from invitation record
            3. Creates user with inherited floor data
            4. Stores floor in user.flat_floor field
            5. Includes floor in response and welcome email
            
            **Response Includes:**
            - User details with inherited floor information
            - Apartment details with floor context
            - Role assignment (OWNER/TENANT)
            - Registration timestamp
            
            **Automatic Welcome Email:**
            - Beautiful HTML template with floor details
            - Complete flat address including floor
            - Role-specific welcome message
            - Next steps for apartment management
            """,
            tags=["Authentication", "Registration"])
async def flatmate_signup(request: FlatmateSignupRequest, db: Session = Depends(get_db)):
    """Secure flatmate signup with apartment, flat, email and invitation code verification"""
    
    # Step 1: Verify apartment exists and matches the provided apartment_name
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == request.apt_id,
        Apartment.apartment_name == request.apartment_name
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=400,
            detail="Invalid apartment details. Please check apartment name and ID."
        )
    
    # Step 2: Find valid invitation with comprehensive verification
    invitation = db.query(FlatmateInvitation).filter(
        FlatmateInvitation.apartment_id == request.apt_id,
        FlatmateInvitation.flat_number == request.flat_number,
        FlatmateInvitation.invited_email == request.email_id,
        FlatmateInvitation.invitation_code == request.unique_code,
        FlatmateInvitation.is_used == 0,
        FlatmateInvitation.expires_at > datetime.utcnow()
    ).first()
    
    if not invitation:
        # Provide specific error messages for better security
        # Check if invitation exists but is expired
        expired_invitation = db.query(FlatmateInvitation).filter(
            FlatmateInvitation.apartment_id == request.apt_id,
            FlatmateInvitation.flat_number == request.flat_number,
            FlatmateInvitation.invited_email == request.email_id,
            FlatmateInvitation.invitation_code == request.unique_code,
            FlatmateInvitation.is_used == 0
        ).first()
        
        if expired_invitation:
            raise HTTPException(
                status_code=400,
                detail="Your invitation code has expired. Please contact the apartment admin for a new invitation."
            )
        
        # Check if invitation exists but is already used
        used_invitation = db.query(FlatmateInvitation).filter(
            FlatmateInvitation.apartment_id == request.apt_id,
            FlatmateInvitation.flat_number == request.flat_number,
            FlatmateInvitation.invited_email == request.email_id,
            FlatmateInvitation.invitation_code == request.unique_code,
            FlatmateInvitation.is_used == 1
        ).first()
        
        if used_invitation:
            raise HTTPException(
                status_code=400,
                detail="This invitation code has already been used. If you need access, please contact the apartment admin."
            )
        
        # Generic error for invalid details
        raise HTTPException(
            status_code=400,
            detail="Invalid invitation details. Please verify apartment ID, flat number, email, and invitation code."
        )
    
    # Step 3: Additional security - verify the invitation was sent by the apartment admin
    if invitation.invited_by_admin_email != apartment.admin_email:
        raise HTTPException(
            status_code=403,
            detail="Security error: Invitation validation failed. Please contact support."
        )
    
    # Step 4: Check if user already exists for this apartment and flat combination
    existing_user = db.query(User).filter(
        User.apartment_id == request.apt_id,
        User.flat_number == request.flat_number
    ).first()
    
    # Step 5: Determine role based on existing users in the flat
    if existing_user:
        # Check if the existing user has the same email (re-registration attempt)
        if existing_user.user_email_id == request.email_id:
            raise HTTPException(
                status_code=400,
                detail="You are already registered for this flat. Please proceed to login."
            )
        
        # There's already someone in this flat, so this person becomes TENANT
        user_role = UserRole.TENANT
        flat_id_prefix = "tenant"
    else:
        # First person in this flat becomes OWNER
        user_role = UserRole.OWNER
        flat_id_prefix = "owner"
    
    # Step 6: Create new user with enhanced flat_id
    user = User(
        flat_id=f"{flat_id_prefix}_{apartment.apartment_id}_{request.flat_number}",
        apartment_uuid=apartment.apartment_uuid,
        apartment_id=apartment.apartment_id,
        user_email_id=request.email_id,
        flat_number=request.flat_number,
        flat_floor=invitation.floor,  # Set floor from invitation
        role=user_role
    )
    
    db.add(user)
    
    # Step 7: Mark invitation as used with timestamp
    invitation.is_used = 1
    invitation.used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # Step 8: Send welcome email
    try:
        send_welcome_email(
            request.email_id,
            apartment.apartment_name,
            request.flat_number,
            user.flat_floor,  # Include floor from user record
            user.role.value
        )
    except Exception as e:
        # Don't fail registration if email fails, just log
        print(f"Failed to send welcome email: {e}")
    
    response_data = {
        "user_id": f"user_{user.id}",
        "flat_id": user.flat_id,
        "flat_uuid": str(user.flat_uuid),
        "apartment_id": apartment.apartment_id,
        "apartment_uuid": str(apartment.apartment_uuid),
        "apartment_name": apartment.apartment_name,
        "flat_number": request.flat_number,
        "flat_floor": user.flat_floor,  # Include floor from user record
        "role": user.role.value,
        "email": user.user_email_id,
        "registration_date": user.created_at.isoformat()
    }
    
    return FlatmateSignupResponse(
        status=True,
        message=f"🎉 Successfully registered! You are now added to {apartment.apartment_name} - Flat {request.flat_number} as {user.role.value.title()}. Please proceed to login.",
        data=response_data
    )

@router.post("/get-apartments", response_model=SelectApartmentResponse,
            summary="Get User Apartments with Floor Information",
            description="""
            Retrieve all apartments where user is registered with comprehensive floor details.
            
            **Enhanced Response:**
            - Complete apartment details with floor information
            - User role in each apartment (ADMIN/OWNER/TENANT)
            - Floor designation for better flat identification
            - Apartment address and contact information
            
            **Floor Information Included:**
            - Native Indian floor conventions (B, G, 1, 2, etc.)
            - Flat number with corresponding floor
            - Role-based access information
            
            **Use Cases:**
            - Apartment selection during login
            - Multi-apartment user management
            - Floor-based apartment organization
            - Role verification across apartments
            """,
            tags=["User Management", "Apartments"])
async def get_user_apartments(request: SelectApartmentRequest, db: Session = Depends(get_db)):
    """Get list of apartments where user is registered"""
    
    # Find all apartments where user is registered
    users = db.query(User).filter(
        User.user_email_id == request.email_id
    ).all()
    
    if not users:
        raise HTTPException(
            status_code=404,
            detail="No apartments found for this email address. Please signup first or check your email."
        )
    
    apartments = []
    for user in users:
        apartment = db.query(Apartment).filter(
            Apartment.apartment_id == user.apartment_id
        ).first()
        
        if apartment:
            apartments.append({
                "apartment_id": apartment.apartment_id,
                "apartment_name": apartment.apartment_name,
                "apartment_address": apartment.apartment_address,
                "flat_number": user.flat_number,
                "flat_floor": user.flat_floor,  # Include floor information
                "role": user.role.value
            })
    
    return SelectApartmentResponse(
        status=True,
        message="Apartments retrieved successfully",
        apartments=apartments
    )

@router.post("/login", response_model=LoginResponse,
            summary="Request Login OTP with Floor Context",
            description="""
            Initiate secure login process with OTP generation and floor-aware email communication.
            
            **Features:**
            - Secure 10-minute OTP generation
            - Beautiful HTML email with floor context
            - User verification with apartment and email validation
            - Floor information included in login email for better identification
            
            **Enhanced Email Experience:**
            - Professional glassmorphism design
            - Floor context: "Flat 101 (Floor: G) | Role: Tenant"
            - Large, readable OTP code display
            - 10-minute expiry timer indication
            - Secure email delivery via Brevo
            
            **Security Features:**
            - Time-limited OTP (10 minutes)
            - One-time use codes
            - Apartment and email verification
            - Automatic cleanup of expired OTPs
            """,
            tags=["Authentication", "OTP"])
async def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    """User selects apartment and email, receives OTP for login"""
    
    # Verify user exists in the selected apartment
    user = db.query(User).filter(
        User.apartment_id == request.apt_id,
        User.user_email_id == request.email_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found in this apartment. Please check your apartment selection or signup first."
        )
    
    # Get apartment details
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == request.apt_id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found"
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 minutes expiry
    
    # Delete any existing OTP for this email/apartment combination
    db.query(OTPVerification).filter(
        OTPVerification.email == request.email_id,
        OTPVerification.apartment_id == request.apt_id
    ).delete()
    
    # Create new OTP record
    otp_record = OTPVerification(
        email=request.email_id,
        apartment_id=request.apt_id,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp_record)
    db.commit()
    
    # Send OTP via email
    try:
        send_login_otp_email(request.email_id, otp_code, apartment.apartment_name, user.flat_number, user.flat_floor, user.role.value)
    except Exception as e:
        # Rollback OTP record if email fails
        db.delete(otp_record)
        db.commit()
        raise e
    
    return LoginResponse(
        status=True,
        message="OTP sent successfully to your email",
        expires_in_minutes=10
    )

@router.post("/assign-additional-tenant", response_model=AssignTenantResponse)
async def assign_additional_tenant(request: AssignTenantRequest, db: Session = Depends(get_db)):
    """Owner can assign an additional tenant to an existing flat (direct assignment without invitation)"""
    
    # Verify apartment exists
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == request.apt_id
    ).first()
    
    if not apartment:
        raise HTTPException(
            status_code=404,
            detail="Apartment not found"
        )
    
    # Check if tenant email already exists in this apartment
    existing_user = db.query(User).filter(
        User.user_email_id == request.tenant_email_id,
        User.apartment_id == request.apt_id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists in this apartment"
        )
    
    # Create new tenant user directly (no invitation process)
    tenant_user = User(
        flat_id=request.flat_id,
        apartment_uuid=apartment.apartment_uuid,
        apartment_id=apartment.apartment_id,
        user_email_id=request.tenant_email_id,
        role=UserRole.TENANT
    )
    
    db.add(tenant_user)
    db.commit()
    db.refresh(tenant_user)
    
    # Send notification email to tenant
    try:
        send_invitation_email(request.tenant_email_id, apartment.apartment_name, request.flat_id)
    except Exception as e:
        # Don't rollback user creation if email fails, just log the error
        print(f"Failed to send tenant assignment email: {e}")
    
    response_data = {
        "tenant_user_id": f"user_{tenant_user.id}",
        "flat_id": tenant_user.flat_id,
        "flat_uuid": str(tenant_user.flat_uuid),
        "tenant_email": tenant_user.user_email_id,
        "apartment_id": apartment.apartment_id,
        "role": tenant_user.role.value
    }
    
    return AssignTenantResponse(
        status=True,
        message="Additional tenant assigned successfully to the flat",
        data=response_data
    )

def send_invitation_email(email: str, apartment_name: str, flat_id: str):
    """Send invitation email to tenant"""
    if not BREVO_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Email service not configured. Please set BREVO_API_KEY environment variable."
        )
    
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    subject = f"🏠 Welcome to FlatFund - {apartment_name}"
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FlatFund Invitation</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 32px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }}
            
            .apartment-name {{
                font-size: 20px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 8px;
            }}
            
            .flat-info {{
                font-size: 16px;
                color: #6B7280;
                font-weight: 500;
            }}
            
            .welcome-note {{
                background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
                border-radius: 12px;
                padding: 20px;
                margin: 24px 0;
                border-left: 4px solid #3B82F6;
            }}
            
            .welcome-text {{
                color: #1E40AF;
                font-size: 14px;
                line-height: 1.6;
            }}
            
            .footer {{
                background: #F9FAFB;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #E5E7EB;
            }}
            
            .footer-text {{
                color: #6B7280;
                font-size: 14px;
                margin-bottom: 16px;
            }}
            
            .company-info {{
                color: #9CA3AF;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">🏢 FlatFund</div>
                <div class="header-subtitle">You've been invited!</div>
            </div>
            
            <div class="content">
                <div class="greeting">Welcome to FlatFund! 🎉</div>
                
                <div class="message">
                    You have been invited as a tenant to join the apartment management system.
                    You can now access your apartment dashboard and manage your flat.
                </div>
                
                <div class="apartment-info">
                    <div class="apartment-name">🏠 {apartment_name}</div>
                    <div class="flat-info">📍 Flat ID: {flat_id}</div>
                </div>
                
                <div class="welcome-note">
                    <div class="welcome-text">
                        <strong>🔐 Getting Started:</strong><br>
                        You can now sign in to FlatFund using this email address. 
                        Simply request an OTP and start managing your flat expenses and communications.
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-text">
                    Welcome to the community!<br>
                    <strong>The FlatFund Team</strong>
                </div>
                
                <div class="company-info">
                    This invitation was sent by your apartment owner.<br>
                    © 2025 FlatFund. All rights reserved.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    sender = {"name": "FlatFund Team", "email": "team.nulltheory@gmail.com"}
    to = [{"email": email}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        sender=sender,
        subject=subject
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"Exception when calling SMTPApi->send_transac_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send invitation email")


def get_current_user_from_token(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """
    Get current user from JWT token in Authorization header
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        flat_id: str = payload.get("sub")
        if flat_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.flat_id == flat_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.put("/updateflatmatedetails", response_model=UpdateFlatmateDetailsResponse)
def update_flatmate_details(
    request: UpdateFlatmateDetailsRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Update user details (name, phone number, flat number, and flat floor) for authenticated user
    """
    # Get current user from JWT token
    current_user = get_current_user_from_token(authorization, db)
    
    # Update user details
    current_user.user_name = request.user_name
    current_user.user_phone_number = request.user_phone_number
    
    # Update flat details if provided
    if request.flat_number is not None:
        current_user.flat_number = request.flat_number
    if request.flat_floor is not None:
        current_user.flat_floor = request.flat_floor
    
    # Check if all required details are now filled
    is_all_user_details_filled = bool(
        current_user.user_name and 
        current_user.user_phone_number and 
        current_user.flat_number is not None and 
        current_user.flat_floor is not None
    )
    
    try:
        db.commit()
        db.refresh(current_user)
        
        return UpdateFlatmateDetailsResponse(
            message="User details updated successfully",
            user_name=current_user.user_name,
            user_phone_number=current_user.user_phone_number,
            flat_number=current_user.flat_number,
            flat_floor=current_user.flat_floor,
            is_all_user_details_filled=is_all_user_details_filled
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user details")


@router.get("/flatmatedetails", response_model=GetFlatmateDetailsResponse)
def get_flatmate_details(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get current user details from JWT token
    """
    # Get current user from JWT token
    current_user = get_current_user_from_token(authorization, db)
    
    # Get apartment details
    apartment = db.query(Apartment).filter(
        Apartment.apartment_id == current_user.apartment_id
    ).first()
    
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    return GetFlatmateDetailsResponse(
        user_name=current_user.user_name,
        user_phone_number=current_user.user_phone_number,
        user_email=current_user.user_email_id,
        flat_id=current_user.flat_id,
        apartment_name=apartment.apartment_name,
        apartment_address=apartment.apartment_address,
        flat_number=current_user.flat_number,
        flat_floor=current_user.flat_floor,
        role=current_user.role.value,
        is_all_user_details_filled=bool(
            current_user.user_name and 
            current_user.user_phone_number and 
            current_user.flat_number is not None and 
            current_user.flat_floor is not None
        )
    )
