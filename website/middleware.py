"""
website/middleware.py

Maintenance mode middleware for NextZenDev.
Checks GlobalSettings.site_online on every request.
"""


class MaintenanceModeMiddleware:
    """
    - If site_online = True  → request passes through normally.
    - If site_online = False → shows maintenance.html (HTTP 503)
      for all URLs EXCEPT /admin/ and whitelisted bypass IPs.
    """

    ALWAYS_ALLOW = ('/admin/',)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Admin is always accessible
        if any(request.path.startswith(p) for p in self.ALWAYS_ALLOW):
            return self.get_response(request)

        from .models import GlobalSettings
        gs = GlobalSettings.get_settings()

        if not gs.site_online:
            visitor_ip = self._get_client_ip(request)
            if visitor_ip not in gs.get_bypass_ips():
                from django.shortcuts import render
                return render(
                    request,
                    'website/maintenance.html',
                    {'gs': gs},
                    status=503,
                )

        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')