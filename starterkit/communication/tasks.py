import logging
from celery import shared_task
from django.contrib.auth import get_user_model
User = get_user_model()

log = logging.getLogger(__name__)


@shared_task
def send_password_reset_email(to_email, source):
    user = User.objects.get(email__iexact=to_email)
    # send email