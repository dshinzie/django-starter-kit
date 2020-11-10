import os
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response


# Validate avatar file extensions
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.svg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


def exception_handler(exception, context=None):
    error = StarterError(exception)
    response = error.format_response()
    return response


class StarterError:

    def __init__(self, exception):
        self._exception = exception
        try:
            if isinstance(exception, APIException):
                self.status_code = exception.status_code
                self.code = exception.default_code
                self.message = exception.default_detail
                self.details = exception.get_full_details()
            else:
                self.status_code = exception.status_code
                self.code = exception.code
                self.message = exception.message
                self.details = exception.details
        except:
            self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.code = 'Internal Server Error'
            self.message = f'{exception}'
            self.details = exception.__dict__

    def format_response(self):
        data = {
            'code': self.code,
            'message': self.message,
            'details': self.details
        }
        headers = {}
        if getattr(self._exception, 'auth_header', None):
            headers['WWW-Authenticate'] = self._exception.auth_header
        if getattr(self._exception, 'wait', None):
            headers['Retry-After'] = f'{self._exception.wait}'

        return Response(data, status=self.status_code, headers=headers)
