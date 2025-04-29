# contact_api/views.py

import json
from django.http import JsonResponse, HttpResponseBadRequest
# CSRF Exempt is removed
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactSubmission # Import the model

@require_POST # Only allow POST
def contact_api_view(request):
    # CSRF token check is handled by middleware

    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if not all([name, email, subject, message]):
            return HttpResponseBadRequest(json.dumps({'status': 'error', 'message': 'Missing required fields.'}), content_type='application/json')

        print(f"Received Contact Form Submission from {name} ({email})") # Log basic info

        # --- Save to Database ---
        try:
            submission = ContactSubmission.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            print(f"Contact submission saved to DB with ID: {submission.id}")
        except Exception as e:
            print(f"CRITICAL: Error saving contact submission to database: {e}")
            return JsonResponse({'status': 'error', 'message': 'Failed to save your submission.'}, status=500)

        # --- Attempt to Send Email Notification ---
        try:
            send_mail(
                f'IndSpice Contact Form: {subject}',
                f'Message received (and saved to DB):\n\nFrom: {name}\nReply-To Email: {email}\nSubject: {subject}\n\nMessage:\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                settings.ADMIN_EMAIL, # Use ADMIN_EMAIL list from settings
                fail_silently=False,
            )
            print("Email notification sent successfully.")
        except Exception as e:
            print(f"WARNING: Error sending email notification (submission WAS saved): {e}")
            # Don't fail the whole request just because email failed, as data is saved

        # --- Return Success Response ---
        return JsonResponse({'status': 'success', 'message': 'Message received and stored successfully!'})

    except json.JSONDecodeError:
        return HttpResponseBadRequest(json.dumps({'status': 'error', 'message': 'Invalid submission format.'}), content_type='application/json')
    except Exception as e:
        print(f"ERROR: Unexpected error processing contact submission: {e}")
        return JsonResponse({'status': 'error', 'message': 'An internal server error occurred.'}, status=500)