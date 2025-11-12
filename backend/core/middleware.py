from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import DisallowedHost


class AllowAllHostsMiddleware(MiddlewareMixin):
    """Allow all hosts in production (Railway) by bypassing ALLOWED_HOSTS check"""
    
    def process_request(self, request):
        # In production (Railway), bypass host validation
        # This middleware should be placed before CommonMiddleware
        return None
    
    def process_exception(self, request, exception):
        # Catch DisallowedHost and allow it in production
        if isinstance(exception, DisallowedHost):
            import os
            if os.environ.get('PORT'):  # Railway sets PORT
                return None  # Allow the request to proceed
        return None
