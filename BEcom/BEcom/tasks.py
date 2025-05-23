from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User 

@shared_task
def send_welcome_email_task(user_id):
    """
    Sends a welcome email to the user.
    """
    try:
        user = User.objects.get(pk=user_id) 
        subject = 'Welcome to Our Awesome Site!'
        message = f'Hi {user.username},\n\nThank you for signing up for our site. We are excited to have you!'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)
        return f"Welcome email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with id {user_id} not found."
    except Exception as e:
        # TODO: SPECIFIC ERROR LOGGING
        return f"Failed to send email to user_id {user_id}: {str(e)}"