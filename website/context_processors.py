from .models import SocialMedia, SiteSettings

def social_links(request):
    return {
        'social_links': SocialMedia.objects.filter(is_active=True)
    }

def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
    except Exception:
        settings = None
    return {'site_settings': settings}