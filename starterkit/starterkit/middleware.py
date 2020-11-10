from django.conf import settings
from django.http import JsonResponse
from .models import StarterAPIKey
from .utils import exception_handler
from .exceptions import InvalidApiKeyException, MissingApiKeyException


class ApiKeyMiddleware:
    """
    Middleware to enforce all requests in deployed apps have an API key.
    Endpoints that need to be accessed without a key are whitelisted below. 
    """

    paths = [
        '/healthz/',
        '/oauth2/authorize/',
        '/oauth2/token/',
        '/user/membership/stripe-webhook/',
    ]

    def __init__(self, process_request):
        self.process_request = process_request

    def __call__(self, request):
        api_key = request.META.get('HTTP_API_KEY')
        # allow all admin pages and static files to be accessed
        if request.path in self.paths or '/admin/' in request.path:
            return self.process_request(request)

        # deployed apps must have an API key for all requests
        if not settings.DEBUG and not api_key:
            response = exception_handler(MissingApiKeyException())
            return JsonResponse(response.data, status=response.status_code)

        if api_key:
            try:
                request.api_key = StarterAPIKey.objects.get(key=api_key)
            except StarterAPIKey.DoesNotExist:
                # API keys are not enforced for local development
                if not settings.DEBUG:
                    response = exception_handler(InvalidApiKeyException(details={'Api-Key': api_key}))
                    return JsonResponse(response.data, status=response.status_code)
        return self.process_request(request)