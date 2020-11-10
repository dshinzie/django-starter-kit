import logging
from django.core.mail import EmailMultiAlternatives, get_connection
from rest_framework.authentication import TokenAuthentication
from rest_framework_api_key.permissions import BaseHasAPIKey
from .models import StarterAPIKey

log = logging.getLogger(__name__)


# Custom authentication
class BearerAuthentication(TokenAuthentication):
    keyword = 'Bearer'
            

class HasAPIKey(BaseHasAPIKey):
    model = StarterAPIKey

    def get_key(self, request):
        return request.META.get('HTTP_API_KEY')


class StarterEmailMultiAlternatives(EmailMultiAlternatives):
    """
    Custom EmailMultiAlternatives to send context to email backend via get_connection()
    """
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, alternatives=None,
                 cc=None, reply_to=None, context=None):
        super(EmailMultiAlternatives, self).__init__(
            subject, body, from_email, to, bcc, connection, attachments,
            headers, cc, reply_to,
        )
        self.alternatives = alternatives or []
        self.context = context or {}

    def get_connection(self, fail_silently=False):
        if not self.connection:
            self.connection = get_connection(fail_silently, **self.context)
        return self.connection
    
    def send_standalone(self, fail_silently=False):
        """Send the email message."""
        if not self.recipients():
            # Don't bother creating the network connection if there's nobody to
            # send to.
            return 0
        return self.get_connection(fail_silently).send_standalone_messages([self])

