# backend/main.py

import os
import smtplib
from email.message import EmailMessage
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv() # Load .env file for local development

# --- Configuration (Read from Environment Variables) ---
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "indspiceorganics@gmail.com")

# === CORRECTED: Use the ENV VARIABLE NAME as the key ===
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD") # Reads env var named GMAIL_APP_PASSWORD
# =======================================================

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"

# === CORRECTED: Read the ENV VARIABLE named CORS_ALLOWED_ORIGINS ===
CORS_ALLOWED_ORIGINS_STRING = os.environ.get('CORS_ALLOWED_ORIGINS', '') # Reads env var named CORS_ALLOWED_ORIGINS
ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS_STRING.split(',') if origin.strip()]
# ==================================================================

IS_DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

if IS_DEBUG:
    if not ALLOWED_ORIGINS: ALLOWED_ORIGINS = []
    local_origin_port = os.environ.get('FRONTEND_PORT', '5173')
    local_origins = [f"http://localhost:{local_origin_port}", f"http://127.0.0.1:{local_origin_port}"]
    for origin in local_origins:
        if origin not in ALLOWED_ORIGINS:
            ALLOWED_ORIGINS.append(origin)

# --- Check for critical missing production configurations ---
if not IS_DEBUG:
    # Check if the variables were successfully read from the environment
    if not GMAIL_USER: raise ValueError("GMAIL_USER environment variable not set!")
    if not GMAIL_APP_PASSWORD: raise ValueError("GMAIL_APP_PASSWORD environment variable not set!")
    if not ALLOWED_ORIGINS: raise ValueError("CORS_ALLOWED_ORIGINS environment variable not set or empty!")
# -----------------------------------------------------------

# --- Pydantic Model ---
class ContactForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
# --------------------

# --- FastAPI app instance ---
app = FastAPI(
    title="IndSpice Organics Contact API",
    description="API endpoint to handle contact form submissions.",
    version="1.0.0",
)
# ---------------------------

# --- Add CORS Middleware ---
if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["POST", "GET", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    # This warning is important, especially for production
    print("WARNING: CORS_ALLOWED_ORIGINS environment variable not set or empty. CORS middleware not fully configured.")
# ---------------------------

# --- Define the API Endpoint ---
@app.post("/api/contact/", status_code=status.HTTP_200_OK)
async def handle_contact_form(contact_data: ContactForm):
    print(f"Received contact data from: {contact_data.email}")

    # Check again specifically within the request context for safety
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
         print("CRITICAL SERVER ERROR: Email sending credentials not available.")
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server email configuration error.")

    # Prepare email content (no changes here)
    msg = EmailMessage()
    # ... (set content, Subject, From, To, Reply-To as before) ...
    msg.set_content(f"You received a new message via the IndSpice Organics contact form:\n\nFrom: {contact_data.name}\nReply-To Email: {contact_data.email}\n\nSubject: {contact_data.subject}\n\nMessage:\n{contact_data.message}")
    msg['Subject'] = f'IndSpice Contact Form: {contact_data.subject}'
    msg['From'] = GMAIL_USER
    msg['To'] = ADMIN_EMAIL
    msg['Reply-To'] = contact_data.email


    # Send email (no changes here)
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            if EMAIL_USE_TLS: server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD) # Use the variables read from env
            server.send_message(msg)
        print("Email notification sent successfully via FastAPI.")
        return {"status": "success", "message": "Message sent successfully!"}
    except smtplib.SMTPAuthenticationError:
        print(f"ERROR: SMTP Authentication failed for user {GMAIL_USER}. Check App Password/Account Settings.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send message due to server authentication error.")
    except Exception as e:
        print(f"ERROR: Failed to send email: {type(e).__name__} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while sending the message.")
# ---------------------------

# --- Root endpoint ---
@app.get("/")
async def root():
    return {"message": "Welcome to IndSpice Organics API"}
# --------------------