import logging
from django.conf import settings
from celery import shared_task
User = settings.AUTH_USER_MODEL

log = logging.getLogger(__name__)


@shared_task
def send_password_reset_email(to_email, source):
    user = User.objects.get(email__iexact=to_email)
    # send email