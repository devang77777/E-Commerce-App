from django.http import HttpResponse

class PermissionsPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Allow unload event for all origins to fix the violation
        response['Permissions-Policy'] = "unload=(*)"
        return response
