# backend/main.py

import os
import smtplib
from email.message import EmailMessage
from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field # Field for potential length limits
from dotenv import load_dotenv # Load .env file for local development

# --- Load Environment Variables ---
# Load from .env file only if it exists (for local development)
load_dotenv()

# Configuration (using os.environ.get with defaults for safety)
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "default_admin@example.com")
GMAIL_USER = os.environ.get("GMAIL_USER") # REQUIRED for sending
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD") # REQUIRED for sending
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"

# CORS Origins (Read from env var, split by comma)
CORS_ALLOWED_ORIGINS_STRING = os.environ.get('CORS_ALLOWED_ORIGINS', '')
ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS_STRING.split(',') if origin.strip()]

# Add localhost for local debugging if needed (check DEBUG flag concept)
# You might set a general DEBUG env var like DJANGO_DEBUG was used
IS_DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
if IS_DEBUG:
    # Ensure ALLOWED_ORIGINS is initialized if empty
    if not ALLOWED_ORIGINS:
        ALLOWED_ORIGINS = [] # Initialize if it was empty/not set
    # Add local frontend dev origins
    local_origin = f"http://localhost:{os.environ.get('FRONTEND_PORT', '5173')}"
    local_origin_ip = f"http://127.0.0.1:{os.environ.get('FRONTEND_PORT', '5173')}"
    if local_origin not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(local_origin)
    if local_origin_ip not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(local_origin_ip)

# Check if essential email config is missing in production
if not IS_DEBUG:
    if not GMAIL_USER: raise ValueError("GMAIL_USER environment variable not set!")
    if not GMAIL_APP_PASSWORD: raise ValueError("GMAIL_APP_PASSWORD environment variable not set!")
    if not ALLOWED_ORIGINS: raise ValueError("CORS_ALLOWED_ORIGINS not configured correctly!")

# -----------------------------------------------------

# --- Pydantic Model for Request Body Validation ---
class ContactForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr # Pydantic automatically validates email format
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
# ------------------------------------------------

# --- Create FastAPI app instance ---
# Add details for automatic OpenAPI docs (optional but nice)
app = FastAPI(
    title="IndSpice Organics Contact API",
    description="API endpoint to handle contact form submissions.",
    version="1.0.0",
)
# -----------------------------------

# --- Add CORS Middleware ---
if ALLOWED_ORIGINS: # Only add middleware if there are allowed origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS, # Use the configured list
        allow_credentials=True, # Allow cookies if needed later
        allow_methods=["POST", "GET", "OPTIONS"], # Allow GET for root, OPTIONS for preflight
        allow_headers=["*"], # Allow common headers
    )
else:
    print("WARNING: No CORS_ALLOWED_ORIGINS configured. CORS Middleware not added.")
# ---------------------------

# --- Define the API Endpoint ---
@app.post("/api/contact/", status_code=status.HTTP_200_OK)
async def handle_contact_form(contact_data: ContactForm): # Data automatically validated by Pydantic
    """
    Receives validated contact form data via POST request,
    sends an email notification, and returns a success response.
    """
    print(f"Received contact data: {contact_data.model_dump()}") # Log received data

    # --- Send Email ---
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
         print("ERROR: Email credentials not configured.")
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server email configuration error."
         )

    msg = EmailMessage()
    msg.set_content(
        f"You received a new message via the IndSpice Organics contact form:\n\n"
        f"From: {contact_data.name}\n"
        f"Reply-To Email: {contact_data.email}\n\n"
        f"Subject: {contact_data.subject}\n\n"
        f"Message:\n{contact_data.message}"
    )
    msg['Subject'] = f'IndSpice Contact Form: {contact_data.subject}'
    msg['From'] = GMAIL_USER
    msg['To'] = ADMIN_EMAIL
    msg['Reply-To'] = contact_data.email

    try:
        # Using synchronous smtplib for simplicity here.
        # For very high traffic, consider async email libraries (e.g., aiosmtplib)
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            if EMAIL_USE_TLS:
                server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print("Email notification sent successfully via FastAPI.")
        return {"status": "success", "message": "Message sent successfully!"} # Return JSON success
    except smtplib.SMTPAuthenticationError:
        print("ERROR: SMTP Authentication failed. Check GMAIL_USER/GMAIL_APP_PASSWORD.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message due to server authentication error."
        )
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while sending the message."
        )
# ---------------------------

# --- Root endpoint for health check/basic info ---
@app.get("/")
async def root():
    return {"message": "Welcome to IndSpice Organics API"}
# ----------------------------------------------------

# --- How to run locally for development ---
# 1. Create a .env file in the backend directory with:
#    GMAIL_USER=indspiceorganics@gmail.com
#    GMAIL_APP_PASSWORD=your_google_app_password
#    CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
#    ADMIN_EMAIL=info@indspiceorganics.com # Or your test email
#    DEBUG=True # Optional: to enable local origins in CORS
#    FRONTEND_PORT=5173 # Optional: if not default
# 2. Run: uvicorn main:app --reload --port 8000