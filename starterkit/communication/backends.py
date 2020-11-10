import base64
import logging
import mandrill
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.conf import settings


log = logging.getLogger(__name__)


class MandrillEmailBackend(BaseEmailBackend):

    def __init__(self, *args, **kwargs):
        self.client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
        self.email_template = kwargs.get('email_template')
        self.email_tag = kwargs.get('email_tag')
        self.merge_tags = kwargs.get('merge_tags')
        self.merge_content = kwargs.get('merge_content')
        self.from_name = kwargs.get('from_name', settings.DEFAULT_FROM_NAME)
        super(MandrillEmailBackend, self).__init__(*args, **kwargs)
    
    def _set_mandrill_vars(self):
        merge_vars = []
        for key in self.merge_content:
            merge_vars.append(
                {
                    'content': self.merge_content.get(key),
                    'name': self.merge_tags.get(key)
                }
            )
        return merge_vars

    def close(self):
        pass

    def send_messages(self, email_messages):
        if not email_messages:
            return

        num_sent = 0
        for message in email_messages:
            sent = self.send(message)
            if sent:
                num_sent += sent
        return num_sent

    def send_standalone_messages(self, email_messages):
        if not email_messages:
            return

        num_sent = 0
        for message in email_messages:
            sent = self.send_standalone(message)
            if sent:
                num_sent += sent
        return num_sent

    def send(self, email_message):
        if not email_message.recipients():
            log.error("Error adding recipients to email.")
            return 0

        if not self.client:
            log.error("Error initializing Mandrill client.")
            return 0
        
        if not self.merge_content or not self.email_template or not self.merge_tags:
            log.error("Error sending context to MandrillEmailBackend.")
            return 0

        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        message = email_message.message()
        num_sent = 0
        for to in recipients:
            errors = []
            try:
                message = {
                    'from_email': from_email,
                    'from_name': self.from_name,
                    'merge_language': 'mailchimp',
                    'merge_vars': [
                        {   
                            'rcpt': to,
                            'vars': self._set_mandrill_vars()
                        }
                    ],
                    'subject': email_message.subject,
                    'tags': [self.email_tag],
                    'to': [{'email': to, 'name': to, 'type': 'to'}],
                }
                result = self.client.messages.send_template(
                    template_name=self.email_template,
                    template_content=[],
                    message=message
                    )
                log.info(result)
            except mandrill.Error as e:
                log.exception(f"Error sending Mandrill email: {email_message.subject}, {to}, {e}")
                errors.append(e)
            except Exception as e:
                log.exception("Error with MandrillEmailBackend: {e}")
                errors.append(e)
            else:
                num_sent += 1

        if errors and not self.fail_silently:
            raise errors[0]

        return num_sent
    
    def send_standalone(self, email_message):
        if not email_message.recipients():
            log.error("Error adding recipients to email.")
            return 0

        if not self.client:
            log.error("Error initializing Mandrill client.")
            return 0

        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        attachments = [ {'name': name, 'content': str(base64.b64encode(content.encode('utf-8')), 'utf-8'), 'type': type } for name, content, type in email_message.attachments ]
        num_sent = 0
        for to in recipients:
            errors = []
            try:
                message = {
                    'from_email': from_email,
                    'from_name': self.from_name,
                    'subject': email_message.subject,
                    'text': email_message.body,
                    'attachments': attachments,
                    'tags': [self.email_tag],
                    'to': [{'email': to, 'name': to, 'type': 'to'}],
                }
                result = self.client.messages.send(message=message)
                log.info(result)
            except mandrill.Error as e:
                log.exception(f"Error sending Mandrill email: {email_message.subject}, {to}, {e}")
                errors.append(e)
            except Exception as e:
                log.exception("Error with MandrillEmailBackend: {e}")
                errors.append(e)
            else:
                num_sent += 1

        if errors and not self.fail_silently:
            raise errors[0]

        return num_sent
