# contact_api/views.py

import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings

@csrf_exempt # TEMPORARY for easy testing
@require_POST
def contact_api_view(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if not all([name, email, subject, message]):
            return HttpResponseBadRequest(json.dumps({'status': 'error', 'message': 'Missing required fields.'}), content_type='application/json')

        print(f"Received Contact Form Submission:")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  Subject: {subject}")
        print(f"  Message: {message}")

        # Attempt to send email (Requires email settings in settings.py)
        try:
            send_mail(
                f'Contact Form Submission: {subject}',
                f'Message from: {name} <{email}>\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            print("Email notification attempted.") # Doesn't guarantee success without proper setup
        except Exception as e:
            print(f"Error sending email: {e}")
            return JsonResponse({'status': 'error', 'message': 'Failed to send message notification.'}, status=500)

        return JsonResponse({'status': 'success', 'message': 'Message received successfully!'})

    except json.JSONDecodeError:
        return HttpResponseBadRequest(json.dumps({'status': 'error', 'message': 'Invalid JSON format.'}), content_type='application/json')
    except Exception as e:
        print(f"Unexpected error in contact_api_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'An internal server error occurred.'}, status=500)# contact_api/views.py

import json
from django.http import JsonResponse, HttpResponseBadRequest
# from django.views.decorators.csrf import csrf_exempt # <<< REMOVED this import
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
# Import your model if/when you decide to save to database
# from .models import ContactSubmission

# @csrf_exempt # <<< REMOVED this decorator
@require_POST # Still only allow POST requests
def contact_api_view(request):
    # Django's CsrfViewMiddleware will now automatically handle
    # checking for a valid CSRF token in the request header (X-CSRFToken)
    # If the token is invalid or missing, Django returns a 403 Forbidden response.

    try:
        # Attempt to parse JSON data from the request body
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email') # Submitter's email
        subject = data.get('subject')
        message = data.get('message')

        # Basic validation for required fields
        if not all([name, email, subject, message]):
            return HttpResponseBadRequest(json.dumps({'status': 'error', 'message': 'Missing required fields.'}), content_type='application/json')

        # Log reception (optional)
        print(f"Received Contact Form Submission:")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  Subject: {subject}")
        # Avoid printing full message in production logs if sensitive

        # --- Save to Database (Optional - Uncomment if needed) ---
        # try:
        #     submission = ContactSubmission.objects.create(...)
        #     print(f"Contact submission saved to DB with ID: {submission.id}")
        # except Exception as e:
        #     print(f"Error saving contact submission to database: {e}")
        #     return JsonResponse({'status': 'error', 'message': 'Failed to save submission.'}, status=500)

        # --- Attempt to Send Email Notification ---
        try:
            send_mail(
                f'IndSpice Contact Form: {subject}', # Email subject for admin
                f'You received a new message:\n\n'
                f'From: {name}\n'
                f'Reply-To Email: {email}\n\n' # Submitter's email
                f'Subject: {subject}\n\n'
                f'Message:\n{message}',
                settings.DEFAULT_FROM_EMAIL,    # Sender (from settings)
                [settings.ADMIN_EMAIL],         # Recipient (your email from settings)
                fail_silently=False,            # Raise error if email fails
            )
            print("Email notification attempted.")
        except Exception as e:
            print(f"Error sending email notification: {e}")
            # Return an error to the user if email sending is critical
            return JsonResponse({'status': 'error', 'message': 'Sorry, there was an issue sending your message.'}, status=500)

        # --- Return Success Response ---
        return JsonResponse({'status': 'success', 'message': 'Message received successfully!'})

    except json.JSONDecodeError:
        # Handle cases where the request body isn't valid JSON
        return HttpResponseBadRequest(json.dumps({'status': 'error', 'message': 'Invalid submission format.'}), content_type='application/json')
    except Exception as e:
        # Catch any other unexpected errors during processing
        print(f"Unexpected error processing contact submission: {e}")
        return JsonResponse({'status': 'error', 'message': 'An internal server error occurred.'}, status=500)