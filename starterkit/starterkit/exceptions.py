from rest_framework import exceptions, status


class StarterException(Exception):

    def __init__(
        self,
        message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code='Internal Server Error',
        details=None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class MissingApiKeyException(StarterException):

    def __init__(self, details=None):
        super().__init__(
            message='Missing API key header.',
            status_code=status.HTTP_401_UNAUTHORIZED,
            code='missing_api_key',
            details=details
        )


class InvalidApiKeyException(StarterException):

    def __init__(self, details=None):
        super().__init__(
            message='Invalid API key.',
            status_code=status.HTTP_401_UNAUTHORIZED,
            code='invalid_api_key',
            details=details
        )