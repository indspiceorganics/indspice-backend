# contact_api/models.py

from django.db import models
from django.utils import timezone

class ContactSubmission(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(default=timezone.now)
    responded = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} ({self.email}) - Subject: {self.subject}"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"