from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from functools import wraps
import uuid
import random
import secrets
import hmac
import hashlib
import re
import razorpay
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Lead, LeadNote, PaymentOrder, Invoice  # Assuming these models are defined for CRM and payments
from .models import NewsletterSubscriber
import logging
logger = logging.getLogger(__name__)

from django.db.models import Count, Sum, Q
from django.contrib.admin.views.decorators import staff_member_required
import json
from .models import (
    Contact, ContactLead, Hero, HeroSection, TrustedClient,
    WhyChooseUs, ProcessStep, Testimonial, Service, Portfolio,
    SiteContent, SiteSettings, SocialMedia, ChatSession, ChatMessage, FAQ,
    Coupon, CouponUsage, Referral, Affiliate, AffiliateClick,
    AffiliateConversion, GlobalSettings, PaymentOTP,Client, Project,
    CommunicationLog, Task, EmailTemplate, EmailLog,
)

# ================= DEFAULT DATA =================

DEFAULT_SERVICES = [
    {'title': 'Website Development', 'description': 'Modern responsive websites that convert visitors into customers.'},
    {'title': 'E-commerce', 'description': 'Scalable online stores with payment integration and conversion-driven design.'},
    {'title': 'App Development', 'description': 'Native and cross-platform mobile experiences built for speed and usability.'},
    {'title': 'SEO & Growth', 'description': 'Search-optimized websites and content strategies to attract qualified traffic.'},
    {'title': 'Data Analytics', 'description': 'Transform your data into actionable insights for better business decisions.'},
    {'title': 'Cloud Solutions', 'description': 'Scalable cloud infrastructure and migration services for modern businesses.'},
    {'title': 'Digital Marketing', 'description': 'Strategic marketing campaigns that drive engagement and conversions.'},
    {'title': 'Tech Consulting', 'description': 'Expert guidance to optimize your technology stack and digital strategy.'},
]

DEFAULT_TRUSTED_CLIENTS = [
    {'name': 'Apollo', 'logo_url': 'https://via.placeholder.com/140x70?text=Apollo'},
    {'name': 'Neon Labs', 'logo_url': 'https://via.placeholder.com/140x70?text=Neon+Labs'},
    {'name': 'ZenithX', 'logo_url': 'https://via.placeholder.com/140x70?text=ZenithX'},
    {'name': 'Corebyte', 'logo_url': 'https://via.placeholder.com/140x70?text=Corebyte'},
    {'name': 'HiveTech', 'logo_url': 'https://via.placeholder.com/140x70?text=HiveTech'},
    {'name': 'Nova Studio', 'logo_url': 'https://via.placeholder.com/140x70?text=Nova+Studio'},
]

DEFAULT_WHY_CHOOSE = [
    {'icon': '⚡', 'title': 'Fast Delivery', 'description': 'Quick turnarounds without sacrificing quality.'},
    {'icon': '📈', 'title': 'Scalable Solutions', 'description': 'Systems built to grow with your business.'},
    {'icon': '🔒', 'title': 'Secure Systems', 'description': 'Reliable security practices for every project.'},
    {'icon': '🤝', 'title': 'Expert Team', 'description': 'Dedicated specialists who care about your success.'},
]

DEFAULT_PROCESS_STEPS = [
    {'step_number': 1, 'icon': '📝', 'title': 'Requirement', 'description': 'We listen and document your goals clearly.'},
    {'step_number': 2, 'icon': '🎨', 'title': 'Design', 'description': 'We create polished UI concepts and workflows.'},
    {'step_number': 3, 'icon': '💻', 'title': 'Development', 'description': 'We build fast, scalable digital products.'},
    {'step_number': 4, 'icon': '🚀', 'title': 'Deployment', 'description': 'We launch your project with confidence.'},
]

DEFAULT_TESTIMONIALS = [
    {'name': 'Riya Sharma', 'role': 'CEO, BrightWave', 'feedback': 'NextZenDev delivered our product on time and transformed our digital presence.', 'avatar_url': 'https://via.placeholder.com/100?text=R'},
    {'name': 'Amit Verma', 'role': 'CTO, Pulse Labs', 'feedback': 'The team was responsive, trustworthy, and their work exceeded expectations.', 'avatar_url': 'https://via.placeholder.com/100?text=A'},
    {'name': 'Sanya Patel', 'role': 'Marketing Head, Injecto', 'feedback': 'Professional, creative, and precise. Our website now converts better than ever.', 'avatar_url': 'https://via.placeholder.com/100?text=S'},
]


# ================= COMMON HELPERS =================

def get_site_settings():
    return SiteSettings.objects.first()


def get_gs():
    """Returns the GlobalSettings singleton."""
    return GlobalSettings.get_settings()


def base_context():
    """Common context dict injected into every page."""
    return {
        'site_settings': get_site_settings(),
        'gs': get_gs(),
        'social_links': SocialMedia.objects.filter(is_active=True),
        'nav_services': Service.objects.filter(is_active=True),
    }


# ================= PAGE DISABLED VIEW =================

def page_disabled(request):
    """Shown when a page is turned off via GlobalSettings."""
    return render(request, 'website/page_disabled.html', base_context(), status=404)


# ================= PAGE-ACTIVE DECORATOR =================

def require_page_active(page_flag):
    """
    Decorator — checks GlobalSettings.<page_flag> before running the view.
    If the flag is False, shows the page_disabled page instead.

    Usage:
        @require_page_active('page_services_active')
        def services(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            gs = get_gs()
            if not getattr(gs, page_flag, True):
                return page_disabled(request)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


# ================= PAGE VIEWS =================

def home(request):
    gs = get_gs()

    if not gs.page_home_active:
        return page_disabled(request)

    hero          = HeroSection.objects.filter(is_active=True).order_by('order').first() if gs.section_hero_active else None
    services      = (list(Service.objects.filter(is_active=True).order_by('order')) or DEFAULT_SERVICES) if gs.section_services_active else []
    trusted_clients = (list(TrustedClient.objects.filter(is_active=True).order_by('order')[:6]) or DEFAULT_TRUSTED_CLIENTS) if gs.section_trusted_active else []
    why_choose    = (list(WhyChooseUs.objects.filter(is_active=True).order_by('order')) or DEFAULT_WHY_CHOOSE) if gs.section_why_choose_active else []
    process_steps = (list(ProcessStep.objects.filter(is_active=True).order_by('step_number')) or DEFAULT_PROCESS_STEPS) if gs.section_process_active else []
    testimonials  = (list(Testimonial.objects.filter(is_active=True).order_by('order')[:3]) or DEFAULT_TESTIMONIALS) if gs.section_testimonials_active else []
    portfolio     = Portfolio.objects.filter(is_active=True).order_by('order') if gs.section_portfolio_active else []

    return render(request, 'website/home.html', {
        **base_context(),
        'hero':           hero,
        'services':       services,
        'trusted_clients': trusted_clients,
        'why_choose':     why_choose,
        'process_steps':  process_steps,
        'testimonials':   testimonials,
        'portfolio':      portfolio,
    })


@require_page_active('page_services_active')
def services(request):
    services_list = list(Service.objects.filter(is_active=True).order_by('order')) or DEFAULT_SERVICES
    return render(request, 'website/services.html', {
        **base_context(),
        'services': services_list,
    })


@require_page_active('page_portfolio_active')
def portfolio(request):
    portfolio_qs = Portfolio.objects.filter(is_active=True).order_by('order')
    return render(request, 'website/portfolio.html', {
        **base_context(),
        'portfolio': portfolio_qs,
    })


@require_page_active('page_about_active')
def about(request):
    hero = Hero.objects.first()
    return render(request, 'website/about.html', {
        **base_context(),
        'hero': hero,
    })


@require_page_active('page_contact_active')
def contact(request):
    if request.method == 'POST':
        ref_code = request.POST.get('ref') or request.GET.get('ref', '')
        referral = None
        if ref_code:
            try:
                referral = Referral.objects.get(referral_code=ref_code, status='pending')
            except Referral.DoesNotExist:
                pass

        ContactLead.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            message=request.POST.get('message'),
        )

        # Also save full contact details (service, budget, timeline) to Contact model
        Contact.objects.create(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            service=request.POST.get('service', ''),
            budget=request.POST.get('budget', ''),
            timeline=request.POST.get('timeline', ''),
            message=request.POST.get('message', ''),
        )

        # Common variables (used by both user + admin email)
        user_email = request.POST.get('email', '').strip()
        user_name  = request.POST.get('name', '').strip()
        user_msg   = request.POST.get('message', '').strip()

        # ── User ko confirmation email ────────────────────────────────────
        if user_email:
            try:
                from django.template.loader import render_to_string
                from django.core.mail import EmailMultiAlternatives as _EMA
                _ss            = get_site_settings()
                _support_email = (_ss.email if _ss and _ss.email else settings.DEFAULT_FROM_EMAIL)
                html = render_to_string('website/email_contact_confirm.html', {
                    'name':          user_name,
                    'message':       user_msg,
                    'site_name':     settings.SITE_NAME,
                    'site_url':      getattr(settings, 'SITE_URL', ''),
                    'support_email': _support_email,
                })
                plain = (
                    f"Hi {user_name},\n\n"
                    f"Thanks for contacting {settings.SITE_NAME}! "
                    f"We've received your message and will get back to you within 24 hours.\n\n"
                    f"Your message:\n{user_msg}\n\n"
                    f"Regards,\n{settings.SITE_NAME}"
                )
                mail = _EMA(
                    subject    = f"We received your message — {settings.SITE_NAME}",
                    body       = plain,
                    from_email = settings.DEFAULT_FROM_EMAIL,
                    to         = [user_email],
                )
                mail.attach_alternative(html, 'text/html')
                mail.send(fail_silently=True)
                logger.info(f"[Contact] ✅ Confirmation email sent to {user_email}")
            except Exception as e:
                logger.error(f"[Contact] ❌ Confirmation email failed for {user_email}: {e}")

        # ── Admin ko notification email ───────────────────────────────────
        # NOTE: 8 spaces — outside if user_email, runs always
        try:
            from django.core.mail import EmailMultiAlternatives as _EMA_adm
            _gs           = get_gs()
            _admin_emails = _gs.get_admin_notification_emails()
            _ss           = get_site_settings()
            _admin_url    = getattr(settings, 'SITE_URL', '').rstrip('/') + '/admin/'

            plain_admin = (
                f"New Contact Form Submission!\n\n"
                f"Name    : {user_name}\n"
                f"Email   : {user_email}\n"
                f"Phone   : {request.POST.get('phone', '').strip()}\n"
                f"Service : {request.POST.get('service', '').strip()}\n"
                f"Budget  : {request.POST.get('budget', '').strip()}\n"
                f"Timeline: {request.POST.get('timeline', '').strip()}\n\n"
                f"Message :\n{user_msg}\n\n"
                f"View in Admin: {_admin_url}"
            )
            for _ae in _admin_emails:
                _msg_adm = _EMA_adm(
                    subject    = f'📩 New Contact — {user_name} | {settings.SITE_NAME}',
                    body       = plain_admin,
                    from_email = settings.DEFAULT_FROM_EMAIL,
                    to         = [_ae],
                )
                _msg_adm.send(fail_silently=True)
            logger.info(f"[Contact] ✅ Admin notification sent to {_admin_emails}")
        except Exception as _e:
            logger.error(f"[Contact] ❌ Admin notification failed: {_e}")

        # ── Referral handling ─────────────────────────────────────────────
        if referral:
            if referral.is_expired:
                logger.warning(f'[Referral] Expired link used: {referral.referral_code}')
            else:
                referral.referred_name  = request.POST.get('name', '')
                referral.referred_email = request.POST.get('email', '')
                referral.referred_phone = request.POST.get('phone', '')
                referral.status         = 'converted'
                referral.converted_at   = timezone.now()
                referral.save()
                # Referrer ko congratulations + commission email bhejo
                _send_referral_converted_email(referral)

        return redirect('contact_thankyou')

    ref_code = request.GET.get('ref', '')
    return render(request, 'website/contact.html', {
        **base_context(),
        'ref_code': ref_code,
    })


def contact_thankyou(request):
    """Thank you page shown after contact form submission."""
    return render(request, 'website/contact_thankyou.html', {
        **base_context(),
        'page_title': 'Message Sent!',
    })


def terms(request):
    data = SiteContent.objects.filter(page='terms').first()
    return render(request, 'website/terms.html', {**base_context(), 'data': data})


def privacy(request):
    data = SiteContent.objects.filter(page='privacy').first()
    return render(request, 'website/privacy.html', {**base_context(), 'data': data})


def refund(request):
    data = SiteContent.objects.filter(page='refund').first()
    return render(request, 'website/refund.html', {**base_context(), 'data': data})


# ═══════════════════════════════════════════════════════════════
# COUPON VIEWS
# ═══════════════════════════════════════════════════════════════

@require_page_active('page_coupons_active')
def coupons_page(request):
    """Public coupons page listing active coupons."""
    active_coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now(),
    )
    active_coupons = [c for c in active_coupons if c.max_uses == 0 or c.used_count < c.max_uses]
    # Annotate each coupon with remaining uses so template doesn't need arithmetic
    for c in active_coupons:
        c.uses_left = (c.max_uses - c.used_count) if c.max_uses > 0 else None
    return render(request, 'website/coupons.html', {
        **base_context(),
        'coupons': active_coupons,
    })


@csrf_exempt
def validate_coupon(request):
    """AJAX endpoint to validate a coupon code."""
    if request.method != 'POST':
        return JsonResponse({'valid': False, 'error': 'POST required'})

    # Rate limiting: max 20 attempts per IP per minute
    from django.core.cache import cache
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f'coupon_validate_{ip}'
    attempts = cache.get(cache_key, 0)
    if attempts >= 20:
        return JsonResponse({'valid': False, 'error': 'Too many requests. Please wait a moment.'}, status=429)
    cache.set(cache_key, attempts + 1, timeout=60)

    code = request.POST.get('code', '').strip().upper()
    order_value = float(request.POST.get('order_value', 0) or 0)

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'Invalid coupon code.'})

    is_valid_result, message = coupon.is_valid()
    if not is_valid_result:
        return JsonResponse({'valid': False, 'error': message})

    if order_value < float(coupon.min_order_value):
        return JsonResponse({
            'valid': False,
            'error': f'Minimum order value is ₹{coupon.min_order_value}'
        })

    if coupon.discount_type == 'percent':
        discount = (order_value * float(coupon.discount_value)) / 100
    else:
        discount = float(coupon.discount_value)

    return JsonResponse({
        'valid': True,
        'code': coupon.code,
        'discount_type': coupon.discount_type,
        'discount_value': float(coupon.discount_value),
        'discount_amount': round(discount, 2),
        'final_value': round(order_value - discount, 2),
        'description': coupon.description,
    })


# ═══════════════════════════════════════════════════════════════
# REFERRAL VIEWS
# ═══════════════════════════════════════════════════════════════

def _send_referral_link_email(referral):
    """Referrer ko uska referral link + expiry + single-use warning email karta hai."""
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    try:
        ss       = get_site_settings()
        site     = ss.site_name if ss else getattr(settings, 'SITE_NAME', 'NextZenDev')
        support  = ss.email if (ss and ss.email) else settings.DEFAULT_FROM_EMAIL
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
        ref_link = f"{site_url}/contact/?ref={referral.referral_code}"
        expiry_str = referral.expires_at.strftime('%d %B %Y, %I:%M %p') if referral.expires_at else None

        html_body = render_to_string('website/email_referral_link.html', {
            'name':               referral.referrer_name,
            'ref_link':           ref_link,
            'referral_code':      referral.referral_code,
            'reward_description': referral.reward_description or '₹500 credit on your next project',
            'expiry_str':         expiry_str,
            'site_name':          site,
            'site_url':           site_url,
            'support_email':      support,
        })
        plain = (
            f"Hi {referral.referrer_name},\n\nYour referral link is ready!\n\n"
            f"Link : {ref_link}\nCode : {referral.referral_code}\n"
            f"⚠️  Single Use Only — valid for ONE customer\n"
            + (f"⏰  Expires: {expiry_str}\n" if expiry_str else "")
            + f"\nReward: {referral.reward_description or '₹500 credit'}\n\n— {site}"
        )
        msg = EmailMultiAlternatives(
            subject    = f"🔗 Your Referral Link is Ready — {site}",
            body       = plain,
            from_email = settings.DEFAULT_FROM_EMAIL,
            to         = [referral.referrer_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        logger.info(f'[Referral] ✅ Link email sent to {referral.referrer_email}')
    except Exception as e:
        logger.error(f'[Referral] ❌ Link email FAILED for {referral.referrer_email}: {e}', exc_info=True)


def _send_referral_converted_email(referral):
    """Jab referral convert ho — referrer ko congratulations + commission email."""
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    try:
        ss       = get_site_settings()
        site     = ss.site_name if ss else getattr(settings, 'SITE_NAME', 'NextZenDev')
        support  = ss.email if (ss and ss.email) else settings.DEFAULT_FROM_EMAIL
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')

        html_body = render_to_string('website/email_referral_converted.html', {
            'name':               referral.referrer_name,
            'referred_name':      referral.referred_name or 'your friend',
            'referral_code':      referral.referral_code,
            'reward_description': referral.reward_description or '₹500 credit on your next project',
            'commission_amount':  referral.commission_amount,
            'site_name':          site,
            'site_url':           site_url,
            'support_email':      support,
        })
        plain = (
            f"Hi {referral.referrer_name},\n\n"
            f"🎉 Congratulations! Your referral has been converted!\n\n"
            f"Friend: {referral.referred_name or 'your friend'}\n"
            f"Commission: ₹{referral.commission_amount}\n"
            f"Reward: {referral.reward_description or '₹500 credit'}\n\n"
            f"Our team will process your reward shortly.\n\n— {site}"
        )
        msg = EmailMultiAlternatives(
            subject    = f"🎉 Your Referral Converted! Commission Earned — {site}",
            body       = plain,
            from_email = settings.DEFAULT_FROM_EMAIL,
            to         = [referral.referrer_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        logger.info(f'[Referral] ✅ Converted email sent to {referral.referrer_email}')
    except Exception as e:
        logger.error(f'[Referral] ❌ Converted email FAILED for {referral.referrer_email}: {e}', exc_info=True)


@require_page_active('page_referral_active')
def referral_page(request):
    """Public referral signup page. Email directly bheja jaata hai — naya ho ya purana."""
    success = False
    referral = None

    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if name and email:
            referral, created = Referral.objects.get_or_create(
                referrer_email=email,
                defaults={
                    'referrer_name':  name,
                    'referrer_phone': phone,
                }
            )
            if not created:
                update_fields = []
                if name and referral.referrer_name != name:
                    referral.referrer_name = name
                    update_fields.append('referrer_name')
                if phone and referral.referrer_phone != phone:
                    referral.referrer_phone = phone
                    update_fields.append('referrer_phone')
                if update_fields:
                    referral.save(update_fields=update_fields)

            # Har baar email bhejo (naya ho ya purana — re-send bhi kaam karta hai)
            _send_referral_link_email(referral)
            success = True

    return render(request, 'website/referral.html', {
        **base_context(),
        'success':  success,
        'referral': referral,
    })


# ═══════════════════════════════════════════════════════════════
# AFFILIATE VIEWS
# ═══════════════════════════════════════════════════════════════

@require_page_active('page_affiliate_active')
def affiliate_page(request):
    """Public affiliate application page. Signals handle all emails automatically."""
    success = False

    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        email       = request.POST.get('email', '').strip()
        phone       = request.POST.get('phone', '').strip()
        website     = request.POST.get('website', '').strip()
        company     = request.POST.get('company', '').strip()
        how_promote = request.POST.get('how_promote', '').strip()

        if name and email:
            Affiliate.objects.get_or_create(
                email=email,
                defaults={
                    'name':        name,
                    'phone':       phone,
                    'website':     website,
                    'company':     company,
                    'how_promote': how_promote,
                    'status':      'pending',
                }
            )
            success = True

    return render(request, 'website/affiliate.html', {
        **base_context(),
        'success': success,
    })


def affiliate_track_click(request, aff_code):
    """Track affiliate link click and redirect to homepage."""
    try:
        affiliate = Affiliate.objects.get(affiliate_code=aff_code, status='active')
        AffiliateClick.objects.create(
            affiliate=affiliate,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            landing_page=request.GET.get('to', '/'),
        )
        affiliate.total_clicks += 1
        affiliate.save(update_fields=['total_clicks'])

        # Security: block open redirects — only allow relative paths
        from urllib.parse import urlparse
        raw_redirect = request.GET.get('to', '/')
        parsed = urlparse(raw_redirect)
        # Reject anything with a scheme or netloc (external URL)
        redirect_to = raw_redirect if (not parsed.scheme and not parsed.netloc) else '/'

        response = redirect(redirect_to)
        request.session['aff_code'] = aff_code
        return response
    except Affiliate.DoesNotExist:
        return redirect('/')


# ═══════════════════════════════════════════════════════════════
# AI RECOMMENDATION API
# ═══════════════════════════════════════════════════════════════

@csrf_exempt
def ai_recommend(request):
    """
    AI service recommendation based on project description.
    Returns top 3 recommended services + upsell suggestion.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    project  = request.POST.get('project', '').lower()
    features = request.POST.get('features', '').lower()
    budget   = request.POST.get('budget', '').lower()
    combined = f"{project} {features}"

    SERVICE_KEYWORDS = {
        'Website Development':  ['website', 'web', 'landing page', 'portfolio', 'blog'],
        'E-commerce':           ['shop', 'store', 'ecommerce', 'sell', 'product', 'payment'],
        'App Development':      ['app', 'mobile', 'android', 'ios', 'flutter', 'react native'],
        'SEO & Growth':         ['seo', 'traffic', 'google', 'ranking', 'search', 'organic'],
        'Data Analytics':       ['data', 'analytics', 'dashboard', 'report', 'insights', 'bi'],
        'Cloud Solutions':      ['cloud', 'aws', 'azure', 'hosting', 'server', 'devops', 'docker'],
        'Digital Marketing':    ['marketing', 'ads', 'social media', 'campaign', 'brand'],
        'Tech Consulting':      ['consult', 'strategy', 'audit', 'review', 'advice'],
    }

    UPSELL_MAP = {
        'Website Development': 'Adding SEO & Google Analytics can 3× your leads in 90 days.',
        'E-commerce':          'Pair with Digital Marketing to drive your first 1,000 customers.',
        'App Development':     'Consider Cloud Solutions for auto-scaling at launch.',
        'SEO & Growth':        'Combine with Content Creation for compounding organic growth.',
        'Data Analytics':      'Cloud Solutions can automate your data pipelines for real-time insights.',
        'Cloud Solutions':     'Add monitoring & alerting — ask us about our SLA packages.',
        'Digital Marketing':   'A landing page optimized for conversion can 2× your ad ROI.',
        'Tech Consulting':     'We can follow up with a full tech audit report.',
    }

    scored = {}
    for service, keywords in SERVICE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > 0:
            scored[service] = score

    top_services = sorted(scored, key=scored.get, reverse=True)[:3]
    if not top_services:
        top_services = ['Website Development', 'Digital Marketing']

    upsell = UPSELL_MAP.get(top_services[0], 'Ask our team about bundle discounts!')

    budget_note = ''
    if any(x in budget for x in ['10000', '15000', '20000', '₹10', '₹15', '₹20', 'low', 'small']):
        budget_note = '💡 Tip: Start with MVP — we can scale once you validate the idea.'
    elif any(x in budget for x in ['lakh', '100000', '50000', '₹50', '₹1']):
        budget_note = '🚀 Great budget! We can deliver a full-featured solution with room for custom integrations.'

    return JsonResponse({
        'recommended_services': top_services,
        'upsell': upsell,
        'budget_note': budget_note,
    })


# ================= CHATBOT HELPERS =================

def is_valid(text):
    invalid_inputs = ["hi", "hello", "ok", "hmm", "yes", "no", "okay"]
    return len(text.strip()) > 3 and text.strip().lower() not in invalid_inputs


def get_faq_reply(msg):
    faqs = FAQ.objects.filter(is_active=True)
    msg_lower = msg.lower()
    for faq in faqs:
        if faq.question and faq.question.lower() in msg_lower:
            return faq.answer
    return None


def admin_has_replied(session):
    return session.messages.filter(sender='admin').exists()


# ================= CHATBOT API =================

@csrf_exempt
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    msg        = request.POST.get("message", "").strip()
    session_id = request.POST.get("session_id", "").strip()

    if not session_id:
        session_id = str(uuid.uuid4())
    
    if not msg:
        return JsonResponse({
            "reply":      "👋 Hello! Welcome to " + getattr(settings, 'SITE_NAME', 'us') + ".\n\nWhat would you like to build?\n(e.g. Website / App / Data Solution)",
            "session_id": session_id,
            "flow_state": "greeted",
            "is_ended":   False,
            "admin_active": False,
        })

    session, created = ChatSession.objects.get_or_create(session_id=session_id)
    if created:
        session.flow_state = "greeted"
        session.save()
    # Block all input if conversation has been ended
    if session.is_ended:
        # Save the user message even for ended sessions (audit trail)
        if msg:
            ChatMessage.objects.create(session=session, sender="user", message=msg)
        return JsonResponse({
            "reply": None,
            "session_id": session_id,
            "flow_state": "ended",
            "is_ended": True,
            "admin_active": False,
        })

    if admin_has_replied(session):
        return JsonResponse({
            "reply": None,
            "session_id": session_id,
            "flow_state": session.flow_state,
            "admin_active": True,
        })

    msg_lower = msg.lower()
    reply = ""
    state = session.flow_state

    if state is None:
        _site_name = getattr(settings, 'SITE_NAME', 'us')
        reply = (
            f"👋 Hello! Welcome to {_site_name}.\n\n"
            "What would you like to build?\n"
            "(e.g. Website / App / Data Solution)"
        )
        session.flow_state = "greeted"

    elif state == "greeted":
        if not msg:
            reply = "Please tell me what you want to build 😊"
        elif not is_valid(msg):
            reply = "Please describe what you want to build (e.g. website, mobile app)."
        else:
            faq = get_faq_reply(msg)
            if faq:
                reply = f"😊 {faq}\n\nWould you like to discuss a project? Please tell me more about what you need."
            else:
                session.project = msg
                session.flow_state = "asked_features"
                reply = f"Great choice! 👍\n\nWhat features do you need for your {msg}?"

    elif state == "asked_features":
        if not is_valid(msg):
            reply = "Please describe the features you need 😊"
        else:
            session.features = msg
            session.flow_state = "asked_budget"
            reply = "Got it! 💡\n\nWhat is your approximate budget?"

    elif state == "asked_budget":
        if not is_valid(msg):
            reply = "Please enter a valid budget (e.g. ₹50,000 or $500)."
        else:
            session.budget = msg
            session.flow_state = "asked_timeline"
            reply = "Perfect! ⏰\n\nWhat is your expected timeline?"

    elif state == "asked_timeline":
        if not is_valid(msg):
            reply = "Please enter an expected timeline (e.g. 1 month, 3 weeks)."
        else:
            session.timeline = msg
            session.flow_state = "asked_name"
            reply = "Almost there! 🙌\n\nMay I know your name?"

    elif state == "asked_name":
        if not is_valid(msg):
            reply = "Please enter your name."
        else:
            session.name = msg
            session.flow_state = "asked_mobile"
            reply = f"Nice to meet you, {msg}! 📱\n\nPlease share your mobile number."

    elif state == "asked_mobile":
        if len(msg.strip()) < 7:
            reply = "Please enter a valid mobile number."
        else:
            session.mobile = msg
            session.flow_state = "asked_email"
            reply = "Great! 📧\n\nPlease enter your email address."

    elif state == "asked_email":
        if "@" not in msg or "." not in msg:
            reply = "Please enter a valid email address."
        else:
            session.email = msg
            session.flow_state = "done"
            eta = random.choice([2, 3, 4, 5])
            reply = (
                f"✅ Thank you, {session.name}!\n\n"
                f"Our team will contact you within {eta} minutes.\n"
                "Please keep this chat open — you'll receive a live reply here! 😊"
            )

    elif state == "done":
        faq_reply = get_faq_reply(msg)
        if faq_reply:
            reply = f"😊 {faq_reply}"
        elif "coupon" in msg_lower or "discount" in msg_lower or "offer" in msg_lower:
            reply = "🎁 We have active coupons! Visit /coupons/ to see current offers and save on your project."
        elif "refer" in msg_lower or "referral" in msg_lower:
            reply = "🤝 Our referral program gives you ₹500 credit for every friend you refer! Visit /referral/ to get your link."
        elif "affiliate" in msg_lower:
            reply = "💼 Join our affiliate program and earn commission on every project! Visit /affiliate/ to apply."
        elif "price" in msg_lower or "cost" in msg_lower:
            reply = "💰 Pricing depends on your requirements. Our team will guide you shortly."
        elif "service" in msg_lower:
            reply = "🚀 We provide Website, App & Data Solutions. Our team will be with you shortly!"
        else:
            reply = "Our team has been notified and will respond here shortly. 😊"

    session.save()
    if msg:
        ChatMessage.objects.create(
            session=session,
            sender="user",
            message=msg,
        )
    ChatMessage.objects.create(
        session=session,
        sender="bot",
        message=reply,
        is_resolved=False
    )

    return JsonResponse({
        "reply":        reply,
        "session_id":   session_id,
        "flow_state":   session.flow_state,
        "is_ended":     session.is_ended,
        "admin_active": False,
    })


# ================= FETCH MESSAGES =================

def fetch_messages(request):
    session_id = request.GET.get("session_id")

    if not session_id:
        return JsonResponse({"messages": [], "admin_active": False})

    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return JsonResponse({"messages": [], "admin_active": False})

    messages = ChatMessage.objects.filter(session=session).order_by("created_at")
    data = [{"sender": m.sender, "message": m.message} for m in messages]
    is_admin_active = session.messages.filter(sender='admin').exists()

    return JsonResponse({
        "messages":    data,
        "admin_active": is_admin_active,
        "is_ended":    session.is_ended,
        "ended_by":    session.ended_by or "",
    })


# ================= ADMIN REPLY =================

@csrf_exempt
def admin_reply(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    if request.method == "POST":
        session_id = request.POST.get("session_id")
        message    = request.POST.get("message", "").strip()

        if not message:
            return JsonResponse({"status": "error", "message": "Empty message"})

        try:
            session = ChatSession.objects.get(session_id=session_id)

            # Block reply if conversation already ended
            if getattr(session, 'is_ended', False):
                return JsonResponse({"status": "error", "message": "Conversation has ended"})

            first_admin_reply = not session.messages.filter(sender='admin').exists()
            if first_admin_reply:
                ChatMessage.objects.create(
                    session=session,
                    sender="system",
                    message="🟢 An agent has joined the chat. You are now in live support!",
                    is_resolved=False
                )

            ChatMessage.objects.create(
                session=session,
                sender="admin",
                message=message,
                is_resolved=True
            )

            return JsonResponse({"status": "ok"})

        except ChatSession.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Session not found"})


# ================= END CONVERSATION =================

@csrf_exempt
def end_conversation(request):
    """
    POST: session_id, ended_by ('user' or 'admin')
    Marks the session as ended — both sides see a system message and input is disabled.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    session_id = request.POST.get("session_id", "").strip()
    ended_by   = request.POST.get("ended_by", "user").strip()

    if not session_id:
        return JsonResponse({"status": "error", "message": "session_id required"}, status=400)

    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Session not found"}, status=404)

    # Already ended — idempotent
    if getattr(session, 'is_ended', False):
        return JsonResponse({"status": "already_ended"})

    # Mark as ended
    session.is_ended   = True
    session.ended_by   = ended_by
    session.ended_at   = timezone.now()
    session.flow_state = "ended"
    session.save(update_fields=['is_ended', 'ended_by', 'ended_at', 'flow_state'])

    # System message visible to both sides
    if ended_by == "admin":
        system_msg = "🔴 The agent has ended this conversation. Thank you for chatting with us!"
    else:
        system_msg = "🔴 You have ended this conversation. Thank you! Feel free to start a new chat anytime."

    ChatMessage.objects.create(
        session=session,
        sender="system",
        message=system_msg,
        is_resolved=True
    )

    return JsonResponse({
        "status":   "ended",
        "ended_by": ended_by,
        "ended_at": session.ended_at.isoformat(),
    })
        


"""
Views for:
  1. Lead CRM public capture  (auto-creates Lead from Contact/Chatbot)
  2. Payment page             (Razorpay integration)
  3. Payment verify endpoint  (signature verification + invoice email)
  4. Admin helpers            (used in django-admin via admin.py)

Add these to your existing views.py
"""

import hmac
import hashlib
import json
import razorpay
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

from .models import Lead, LeadNote, PaymentOrder, Coupon


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def get_razorpay_client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


def send_invoice_email(payment: PaymentOrder):
    """Render invoice HTML template and email it to the customer."""
    _ss = SiteSettings.objects.first()
    _support_email = (_ss.email if _ss and _ss.email else settings.DEFAULT_FROM_EMAIL)
    html_body = render_to_string('website/email_invoice.html', {
        'payment': payment,
        'site_name': settings.SITE_NAME,
        'support_email': _support_email,
        'site_url':      getattr(settings, 'SITE_URL', 'https://nextzendev.in'),
    })
    mail = EmailMessage(
        subject=f"Your Invoice {payment.invoice_number} — {settings.SITE_NAME}",
        body=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[payment.customer_email],
    )
    mail.content_subtype = 'html'
    mail.send(fail_silently=True)
    payment.invoice_sent = True
    payment.save(update_fields=['invoice_sent'])


def _send_payment_failed_email(payment: PaymentOrder, reason: str = ''):
    """Send a payment failure notification email to the customer."""
    try:
        from html import escape
        site_name    = getattr(settings, 'SITE_NAME', 'NextZen IT Solutions')
        site_url     = getattr(settings, 'SITE_URL', '').rstrip('/')
        support_mail = settings.DEFAULT_FROM_EMAIL
        amount       = payment.final_amount
        name         = escape(str(payment.customer_name))
        order_id     = escape(str(getattr(payment, 'razorpay_order_id', '') or '—'))
        fail_reason  = escape(str(reason or 'Payment verification failed'))

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Payment Failed</title>
</head>
<body style="margin:0;padding:0;background:#0f1117;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f1117;padding:40px 16px;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0" style="max-width:520px;width:100%;">

        <!-- HEADER -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a1d27 0%,#12151f 100%);border-radius:16px 16px 0 0;padding:36px 40px 28px;text-align:center;border-bottom:1px solid #1e2130;">
            <div style="display:inline-block;background:#ef444420;border:1px solid #ef444440;border-radius:50px;padding:6px 16px;margin-bottom:20px;">
              <span style="color:#ef4444;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;">Payment Alert</span>
            </div>
            <div style="width:64px;height:64px;background:#ef444418;border:2px solid #ef444450;border-radius:50%;margin:0 auto 16px;">
              <p style="color:#f87171;font-size:28px;font-weight:700;margin:0;line-height:64px;text-align:center;">✕</p>
            </div>
            <h1 style="color:#f1f5f9;font-size:22px;font-weight:700;margin:0 0 8px;letter-spacing:-0.3px;">Payment Not Completed</h1>
            <p style="color:#64748b;font-size:13px;margin:0;">We were unable to process your transaction</p>
          </td>
        </tr>

        <!-- BODY -->
        <tr>
          <td style="background:#12151f;padding:32px 40px;">

            <!-- Greeting -->
            <p style="color:#94a3b8;font-size:14px;margin:0 0 24px;line-height:1.6;">
              Hi <strong style="color:#e2e8f0;">{name}</strong>,<br/>
              Unfortunately your payment of <strong style="color:#f87171;">₹{amount}</strong> could not be completed. Please review the details below and try again.
            </p>

            <!-- Amount / Order ID / Status Card -->
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1d27;border:1px solid #1e2130;border-radius:12px;margin-bottom:20px;">
              <tr>
                <td style="padding:20px 24px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td width="33%" style="color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Amount</td>
                      <td width="34%" style="color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Order ID</td>
                      <td width="33%" style="color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Status</td>
                    </tr>
                    <tr>
                      <td style="color:#f87171;font-size:20px;font-weight:700;padding-top:6px;">₹{amount}</td>
                      <td style="color:#94a3b8;font-size:11px;padding-top:8px;font-family:monospace;">{str(order_id)[:20]}</td>
                      <td style="padding-top:6px;">
                        <span style="background:#ef444420;color:#f87171;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.5px;">FAILED</span>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>

            <!-- Reason Box -->
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#1f1318;border:1px solid #ef444430;border-left:3px solid #ef4444;border-radius:8px;margin-bottom:28px;">
              <tr>
                <td style="padding:14px 18px;">
                  <p style="margin:0 0 4px;color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Failure Reason</p>
                  <p style="margin:0;color:#fca5a5;font-size:13px;font-weight:500;">{fail_reason}</p>
                </td>
              </tr>
            </table>

            <!-- CTA Button -->
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
              <tr>
                <td align="center">
                  <a href="{site_url}/payment/" style="display:inline-block;background:linear-gradient(135deg,#6366f1,#4f46e5);color:#fff;text-decoration:none;font-size:14px;font-weight:600;padding:13px 36px;border-radius:8px;letter-spacing:0.3px;">
                    🔄 Try Payment Again
                  </a>
                </td>
              </tr>
            </table>

            <!-- Divider -->
            <div style="border-top:1px solid #1e2130;margin-bottom:24px;"></div>

            <!-- Help -->
            <p style="color:#475569;font-size:13px;text-align:center;margin:0;line-height:1.6;">
              Need help? Reach us at<br/>
              <a href="mailto:{support_mail}" style="color:#6366f1;text-decoration:none;font-weight:500;">{support_mail}</a>
            </p>

          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td style="background:#0d0f18;border-radius:0 0 16px 16px;padding:20px 40px;text-align:center;border-top:1px solid #1e2130;">
            <p style="color:#334155;font-size:11px;margin:0 0 4px;">⚡ {site_name}</p>
            <p style="color:#1e293b;font-size:11px;margin:0;">This is an automated security notification. Please do not reply to this email.</p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

        mail = EmailMessage(
            subject=f"⚠️ Payment Failed — ₹{amount} | {site_name}",
            body=html,
            from_email=support_mail,
            to=[payment.customer_email],
        )
        mail.content_subtype = 'html'
        mail.send(fail_silently=False)
        logger.info(f"[Payment] Failure email sent to {payment.customer_email}")
    except Exception as e:
        logger.error(f"[Payment] Failed email send error for {payment.customer_email}: {e}")


def auto_create_lead(name, email, phone, source, service='', budget='', message=''):
    """
    Called from contact form / chatbot done state to push a lead into CRM.
    Avoids duplicates: if email already has an open lead, skip.
    """
    if email and Lead.objects.filter(email=email, status__in=['new', 'contacted']).exists():
        return None
    lead = Lead.objects.create(
        name=name, email=email, phone=phone,
        source=source, service=service,
        budget=budget, message=message,
        status='new',
    )
    send_new_lead_emails(lead)
    return lead


# ──────────────────────────────────────────────────────────────
# NEWSLETTER
# ──────────────────────────────────────────────────────────────

@csrf_exempt
def subscribe_newsletter(request):
    """POST: email → save subscriber + send welcome email."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    email = request.POST.get('email', '').strip().lower()

    # Basic validation
    import re
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return JsonResponse({'error': 'Please enter a valid email address.'}, status=400)

    # Save or re-activate
    subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
    if not created:
        if subscriber.is_active:
            return JsonResponse({'error': 'You are already subscribed!'}, status=400)
        else:
            subscriber.is_active = True
            subscriber.save(update_fields=['is_active'])

    # Send welcome email
    try:
        from django.core.mail import EmailMessage
        from django.template.loader import render_to_string
        html = render_to_string('website/email_newsletter_welcome.html', {
            'email':      email,
            'site_name':  settings.SITE_NAME,
        })
        mail = EmailMessage(
            subject=f"Welcome to The Engineering Brief — {settings.SITE_NAME}",
            body=html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        mail.content_subtype = 'html'
        mail.send(fail_silently=False)
    except Exception as e:
        logger.error(f"[Newsletter] Welcome email failed for {email}: {e}")
        # Don't fail the subscription — email is optional

    return JsonResponse({'success': True, 'message': "You're subscribed! Welcome aboard 🎉"})


# ──────────────────────────────────────────────────────────────
# PAYMENT PAGE (customer-facing)
# ──────────────────────────────────────────────────────────────

def payment_page(request):
    """
    Public payment page. Accepts optional GET params:
      ?amount=5000&desc=Website+Development&email=...&name=...
    Also shows active coupons for discount.
    """
    from .models import GlobalSettings
    gs = GlobalSettings.get_settings()

    prefill = {
        'name':        request.GET.get('name', ''),
        'email':       request.GET.get('email', ''),
        'phone':       request.GET.get('phone', ''),
        'amount':      request.GET.get('amount', ''),
        'description': request.GET.get('desc', ''),
    }

    active_coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_until__gte=timezone.now(),
    )

    return render(request, 'website/payment.html', {
        **base_context(),   # site_settings, social_links, nav_services sab aa jayega
        'gs': gs,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'prefill': prefill,
        'active_coupons': active_coupons,
    })


# ──────────────────────────────────────────────────────────────
# CREATE ORDER (AJAX — called before Razorpay popup opens)
# ──────────────────────────────────────────────────────────────

@csrf_exempt
def create_payment_order(request):
    """
    POST: name, email, phone, amount (INR), description, coupon_code (optional)
    Returns: razorpay_order_id + key + prefill data
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    name        = request.POST.get('name', '').strip()
    email       = request.POST.get('email', '').strip()
    phone       = request.POST.get('phone', '').strip()
    description = request.POST.get('description', '').strip()
    coupon_code = request.POST.get('coupon_code', '').strip().upper()
    ref_code    = request.POST.get('ref_code', '').strip().upper()

    try:
        amount = float(request.POST.get('amount', 0))
    except ValueError:
        return JsonResponse({'error': 'Invalid amount'}, status=400)

    if amount <= 0:
        return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)

    # ── Apply coupon ──────────────────────────────────────────
    discount_amount = 0
    coupon_obj = None
    if coupon_code:
        try:
            coupon_obj = Coupon.objects.get(code=coupon_code)
            is_valid, msg = coupon_obj.is_valid()
            if is_valid and amount >= float(coupon_obj.min_order_value):
                if coupon_obj.discount_type == 'percent':
                    discount_amount = (amount * float(coupon_obj.discount_value)) / 100
                else:
                    discount_amount = float(coupon_obj.discount_value)
        except Coupon.DoesNotExist:
            pass

    final_amount = max(0, amount - discount_amount)

    # ── Create Razorpay order ─────────────────────────────────
    client = get_razorpay_client()
    rz_order = client.order.create({
        'amount': int(final_amount * 100),   # paise
        'currency': 'INR',
        'payment_capture': 1,
        'notes': {
            'customer_name':  name,
            'customer_email': email,
            'description':    description,
        }
    })

    # ── Save PaymentOrder to DB ───────────────────────────────
    payment = PaymentOrder.objects.create(
        customer_name=name,
        customer_email=email,
        customer_phone=phone,
        description=description,
        amount=amount,
        coupon=coupon_obj,
        discount_amount=discount_amount,
        final_amount=final_amount,
        razorpay_order_id=rz_order['id'],
        status='pending',
    )

    # ── Auto-link / create CRM lead ───────────────────────────
    lead = auto_create_lead(name, email, phone, source='contact_form',
                            service=description, budget=str(amount))
    if lead:
        payment.lead = lead
        payment.save(update_fields=['lead'])

    # ── Link referral if ref_code provided ───────────────────
    if ref_code:
        try:
            referral_obj = Referral.objects.get(referral_code=ref_code, status='pending')
            if not referral_obj.is_expired:
                # Track that this payment came via referral link
                payment.description = (payment.description or '') + f' [Ref: {ref_code}]'
                payment.save(update_fields=['description'])
                logger.info(f'[Payment] Referral code {ref_code} linked to payment {payment.invoice_number}')
        except Referral.DoesNotExist:
            pass

    return JsonResponse({
        'order_id':    rz_order['id'],
        'amount':      int(final_amount * 100),
        'currency':    'INR',
        'key':         settings.RAZORPAY_KEY_ID,
        'name':        name,
        'email':       email,
        'phone':       phone,
        'description': description,
        'payment_db_id': payment.id,
    })


# ──────────────────────────────────────────────────────────────
# VERIFY PAYMENT (AJAX — called after Razorpay success callback)
# ──────────────────────────────────────────────────────────────

@csrf_exempt
def verify_payment(request):
    """
    POST: razorpay_order_id, razorpay_payment_id, razorpay_signature, payment_db_id
    Verifies signature → marks paid → sends invoice email.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    order_id   = request.POST.get('razorpay_order_id', '')
    payment_id = request.POST.get('razorpay_payment_id', '')
    signature  = request.POST.get('razorpay_signature', '')
    db_id      = request.POST.get('payment_db_id', '')

    # ── Signature verification ────────────────────────────────
    generated_sig = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{order_id}|{payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_sig, signature):
        # Mark order as failed if it exists
        try:
            payment = PaymentOrder.objects.get(id=db_id)
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            _send_payment_failed_email(payment, reason='Signature verification failed')
            logger.info(f"[Payment] Failed email sent for order {db_id}")
        except Exception as e:
            logger.error(f"[Payment] Error occurred while handling failed payment for order {db_id}: {e}")
        return JsonResponse({'success': False, 'error': 'Payment verification failed. Please contact support.'}, status=400)

    # ── Update PaymentOrder ───────────────────────────────────
    try:
        payment = PaymentOrder.objects.get(id=db_id)
    except Exception as e:
        logger.error(f"[Payment] Error occurred while fetching payment for order {db_id}: {e}")
        return JsonResponse({'success': False, 'error': 'Order not found. Please contact support.'}, status=404)

    # Prevent double-processing
    if payment.status == 'paid':
        return JsonResponse({
            'success':        True,
            'invoice_number': payment.invoice_number,
            'message':        f'Payment already confirmed! Invoice {payment.invoice_number} was sent to {payment.customer_email}.',
            'redirect_url':   f'/payment/success/?invoice={payment.invoice_number}',
        })

    payment.razorpay_payment_id = payment_id
    payment.razorpay_signature  = signature
    payment.status              = 'paid'
    payment.paid_at             = timezone.now()
    payment.save()
    
    payment.save()

    # ── Auto-create Invoice in admin ──────────────────────────
    try:
        from .models import Invoice, InvoiceItem
        invoice_obj, created = Invoice.objects.get_or_create(
            payment_order=payment,
            defaults={
                'client_name':    payment.customer_name,
                'client_email':   payment.customer_email,
                'client_phone':   payment.customer_phone or '',
                'from_name':      getattr(settings, 'SITE_NAME', ''),
                'from_email':     settings.DEFAULT_FROM_EMAIL,
                'status':         'paid',
                'paid_at':        payment.paid_at,
                'tax_percent':    0,
                'discount':       payment.discount_amount or 0,
            }
        )
        if created:
            InvoiceItem.objects.create(
                invoice     = invoice_obj,
                description = payment.description or 'Service Payment',
                quantity    = 1,
                unit_price  = payment.final_amount,
            )
            invoice_obj.recalculate()   # subtotal, tax, total calculate karega
            logger.info(f"[Payment] Invoice created → {invoice_obj.invoice_number}")
    except Exception as e:
        logger.error(f"[Payment] Invoice auto-create failed: {e}")
    # ─────────────────────────────────────────────────────────

    # ── Increment coupon usage ────────────────────────────────
    if payment.coupon:
        payment.coupon.used_count += 1
        payment.coupon.save(update_fields=['used_count'])

    # ── Update linked lead to Converted ──────────────────────
    if payment.lead:
        payment.lead.status       = 'converted'
        payment.lead.converted_at = timezone.now()
        payment.lead.save(update_fields=['status', 'converted_at'])

    # ── Send invoice email ────────────────────────────────────
    email_sent = False
    try:
        send_invoice_email(payment)
        email_sent = True
    except Exception as e:
        logger.error(f"[Payment] Invoice email failed for {payment.invoice_number}: {e}")

    logger.info(f"[Payment] SUCCESS — Invoice {payment.invoice_number} | ₹{payment.final_amount} | {payment.customer_email}")

    return JsonResponse({
        'success':        True,
        'invoice_number': payment.invoice_number,
        'message':        f'Payment successful! Invoice {payment.invoice_number} sent to {payment.customer_email}.',
        'redirect_url':   f'/payment/success/?invoice={payment.invoice_number}',
        'email_sent':     email_sent,
        'amount':         float(payment.final_amount),
    })


# ──────────────────────────────────────────────────────────────
# PAYMENT SUCCESS PAGE
# ──────────────────────────────────────────────────────────────

def payment_success(request):
    invoice_number = request.GET.get('invoice', '')
    payment = None
    if invoice_number:
        payment = PaymentOrder.objects.filter(invoice_number=invoice_number, status='paid').first()
    return render(request, 'website/payment_success.html', {
        **base_context(),
        'payment': payment,
    })

# ═══════════════════════════════════════════════════════════════
# OTP HELPERS  —  Fully Secure Implementation
# Security layers:
#   ✅ secrets.randbelow()     — CSPRNG (not random.randint)
#   ✅ SHA-256 hashing         — plain OTP never stored in DB
#   ✅ hmac.compare_digest()   — timing-safe comparison
#   ✅ Either email OR phone    — flexible verification
#   ✅ 5 min expiry             — short window
#   ✅ 5 attempts max           — brute force lockout + delete
#   ✅ One-time use             — record deleted after success
#   ✅ Max 3 resends            — resend rate limiting
#   ✅ OTP not in email subject — no leaking in mail headers/logs
# ═══════════════════════════════════════════════════════════════

def _generate_otp() -> str:
    """Cryptographically secure 6-digit OTP via secrets module."""
    return str(secrets.randbelow(900000) + 100000)


def _hash_otp(otp: str) -> str:
    """One-way SHA-256 hash — stored in DB instead of plain OTP."""
    return hashlib.sha256(otp.encode('utf-8')).hexdigest()


def _verify_otp(input_otp: str, stored_hash: str) -> bool:
    """
    Timing-safe comparison using hmac.compare_digest.
    Prevents timing attacks where attacker measures response time.
    """
    if not input_otp or not stored_hash:
        return False
    return hmac.compare_digest(
        _hash_otp(input_otp),
        stored_hash
    )


def _send_email_otp(email: str, otp: str, site_name: str) -> bool:
    """Send OTP via email using HTML template. OTP NOT in subject line (security)."""
    try:
        html_body = render_to_string('website/email_payment_otp.html', {
            'otp':       otp,
            'site_name': site_name,
        })
        mail = EmailMessage(
            subject    = f'[{site_name}] Your Payment Verification Code',
            body       = html_body,
            from_email = settings.DEFAULT_FROM_EMAIL,
            to         = [email],
        )
        mail.content_subtype = 'html'
        mail.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"[OTP] Email send failed to {email}: {e}")
        return False

def _send_sms_otp(phone: str, otp: str, site_name: str) -> bool:
    """Send OTP via SMS. Twilio if configured, else dev console fallback."""
    try:
        twilio_sid   = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        twilio_from  = getattr(settings, 'TWILIO_FROM', None)

        is_configured = (
            twilio_sid and twilio_token and twilio_from
            and not str(twilio_sid).startswith('ACxxx')
        )

        if is_configured:
            try:
                from twilio.rest import Client as TwilioClient
            except ImportError:
                logger.warning("[OTP-SMS] Twilio not installed. Run: pip install twilio")
                logger.warning(f"[OTP-SMS-DEV] Phone {phone} | OTP: {otp}")
                return True
            client = TwilioClient(twilio_sid, twilio_token)
            client.messages.create(
                body=f"[{site_name}] OTP: {otp}. Valid 5 mins. DO NOT share with anyone.",
                from_=twilio_from,
                to=phone if phone.startswith('+') else f'+91{phone}'
            )
            return True
        else:
            logger.warning(f"[OTP-SMS-DEV] Phone {phone} | OTP: {otp}  (Twilio not configured)")
            return True  # Dev fallback — don't block flow
    except Exception as e:
        logger.error(f"[OTP] SMS send failed to {phone}: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# SEND OTP  — POST /payment/send-otp/
# ═══════════════════════════════════════════════════════════════

@csrf_exempt
def send_payment_otp(request):
    """
    POST: email (required), phone (optional), name
    Security:
      - OTP stored as SHA-256 hash (never plain text)
      - secrets.randbelow() for generation
      - Old unverified OTPs cleaned up
      - 5 min expiry
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    email = request.POST.get('email', '').strip().lower()
    phone = request.POST.get('phone', '').strip()
    name  = request.POST.get('name', '').strip()

    # Validate email
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return JsonResponse({'success': False, 'error': 'Please enter a valid email address.'})

    # Validate phone if provided
    if phone and len(re.sub(r'\D', '', phone)) < 10:
        return JsonResponse({'success': False, 'error': 'Please enter a valid 10-digit phone number.'})

    site_name = getattr(settings, 'SITE_NAME', 'NextZenDev')

    # Generate cryptographically secure OTPs
    email_otp = _generate_otp()
    phone_otp = _generate_otp() if phone else None

    # 5 min expiry (reduced from 10 for tighter security)
    expires = timezone.now() + timezone.timedelta(minutes=5)

    # Cleanup — delete all old unverified OTPs for this email
    PaymentOTP.objects.filter(email=email, email_verified=False, phone_verified=False).delete()

    # Store HASHED OTPs — plain text never touches DB
    otp_record = PaymentOTP.objects.create(
        email      = email,
        phone      = phone or '',
        email_otp  = _hash_otp(email_otp),
        phone_otp  = _hash_otp(phone_otp) if phone_otp else '',
        expires_at = expires,
    )

    # Send OTPs
    email_sent = _send_email_otp(email, email_otp, site_name)
    sms_sent   = _send_sms_otp(phone, phone_otp, site_name) if phone and phone_otp else False

    if not email_sent:
        otp_record.delete()
        return JsonResponse({
            'success': False,
            'error': 'Failed to send OTP email. Please check your email address.',
        })

    logger.info(f"[OTP] Sent → email={email} | phone={'yes' if phone else 'no'} | id={otp_record.id}")

    return JsonResponse({
        'success':   True,
        'otp_id':    otp_record.id,
        'sms_sent':  sms_sent,
        'has_phone': bool(phone),
        'message':   f'OTP sent to {email}' + (f' and {phone}' if phone else '') + '. Valid for 5 minutes.',
    })


# ═══════════════════════════════════════════════════════════════
# VERIFY OTP  — POST /payment/verify-otp/
# ═══════════════════════════════════════════════════════════════

@csrf_exempt
def verify_payment_otp(request):
    """
    POST: otp_id, email_otp (optional), phone_otp (optional)

    Security model:
      - Either email OR phone OTP is sufficient to verify
      - Timing-safe hash comparison (hmac.compare_digest)
      - Max 5 attempts → record deleted (brute force lockout)
      - One-time use → record deleted on success
      - Expiry enforced before any comparison
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    otp_id       = request.POST.get('otp_id', '').strip()
    email_otp_in = request.POST.get('email_otp', '').strip()
    phone_otp_in = request.POST.get('phone_otp', '').strip()

    # Must provide at least one OTP
    if not email_otp_in and not phone_otp_in:
        return JsonResponse({
            'success': False,
            'error': 'Please enter at least one OTP (email or phone).',
        })

    # Validate otp_id is numeric to prevent injection
    if not otp_id.isdigit():
        return JsonResponse({'success': False, 'error': 'Invalid OTP session.'})

    try:
        record = PaymentOTP.objects.get(id=otp_id)
    except (PaymentOTP.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'OTP session not found. Please resend OTP.'})

    # ── Expiry check (before attempt increment) ────────────────
    if record.is_expired():
        record.delete()
        return JsonResponse({'success': False, 'error': 'OTP has expired. Please request a new one.'})

    # ── Brute force check ──────────────────────────────────────
    if record.attempts >= 5:
        record.delete()
        logger.warning(f"[OTP] Brute force lockout — id={otp_id} email={record.email}")
        return JsonResponse({'success': False, 'error': 'Too many wrong attempts. Please request a new OTP.'})

    # ── Increment attempts first (before comparison) ───────────
    record.attempts += 1
    record.save(update_fields=['attempts'])

    # ── Timing-safe hash comparisons ──────────────────────────
    email_ok = _verify_otp(email_otp_in, record.email_otp) if email_otp_in and record.email_otp else False
    phone_ok = _verify_otp(phone_otp_in, record.phone_otp) if phone_otp_in and record.phone_otp else False

    # ── Either one passes → verified ──────────────────────────
    if email_ok or phone_ok:
        verified_via = 'email' if email_ok else 'phone'
        record_id    = record.id
        email_addr   = record.email

        # One-time use: delete immediately after success
        record.delete()

        logger.info(f"[OTP] Verified via {verified_via} — id={record_id} email={email_addr}")

        return JsonResponse({
            'success':      True,
            'verified':     True,
            'verified_via': verified_via,
            'message':      'Identity verified successfully! Proceeding to payment.',
        })

    # ── Both wrong ─────────────────────────────────────────────
    remaining = 5 - record.attempts
    if remaining <= 0:
        record.delete()
        return JsonResponse({'success': False, 'error': 'Too many wrong attempts. Please request a new OTP.'})

    logger.warning(f"[OTP] Wrong attempt {record.attempts}/5 — id={otp_id} email={record.email}")

    return JsonResponse({
        'success': False,
        'error':   f'Incorrect OTP. {remaining} attempt(s) remaining.',
    })


# ═══════════════════════════════════════════════════════════════
# RESEND OTP  — POST /payment/resend-otp/
# ═══════════════════════════════════════════════════════════════

@csrf_exempt
def resend_payment_otp(request):
    """
    POST: otp_id
    Security:
      - Max 3 resends per session (rate limiting)
      - Fresh CSPRNG OTPs generated
      - Stored as SHA-256 hash
      - Attempts reset to 0 on resend
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    otp_id = request.POST.get('otp_id', '').strip()

    if not otp_id.isdigit():
        return JsonResponse({'success': False, 'error': 'Invalid OTP session.'})

    try:
        record = PaymentOTP.objects.get(id=otp_id)
    except (PaymentOTP.DoesNotExist, ValueError):
        return JsonResponse({'success': False, 'error': 'Session not found. Please refresh the page.'})

    # ── Resend rate limit ──────────────────────────────────────
    resend_count = getattr(record, 'resend_count', 0) or 0
    if resend_count >= 3:
        return JsonResponse({
            'success': False,
            'error':   'Maximum resend limit reached. Please refresh the page and start again.',
        })

    site_name = getattr(settings, 'SITE_NAME', 'NextZenDev')

    # Fresh CSPRNG OTPs
    new_email_otp = _generate_otp()
    new_phone_otp = _generate_otp() if record.phone else None

    # Store hashed — plain never saved
    record.email_otp      = _hash_otp(new_email_otp)
    record.phone_otp      = _hash_otp(new_phone_otp) if new_phone_otp else ''
    record.attempts       = 0
    record.email_verified = False
    record.phone_verified = False
    record.expires_at     = timezone.now() + timezone.timedelta(minutes=5)

    if hasattr(record, 'resend_count'):
        record.resend_count = resend_count + 1

    record.save()

    email_sent = _send_email_otp(record.email, new_email_otp, site_name)
    sms_sent   = _send_sms_otp(record.phone, new_phone_otp, site_name) if record.phone and new_phone_otp else False

    logger.info(f"[OTP] Resent — id={otp_id} resend_count={resend_count + 1}")

    return JsonResponse({
        'success':  email_sent,
        'sms_sent': sms_sent,
        'message':  'New OTP sent! Valid for 5 minutes.' if email_sent else 'Failed to resend OTP.',
    })


# ═══════════════════════════════════════════════════════════════
# EMAIL AUTOMATION HELPERS
# ═══════════════════════════════════════════════════════════════

def _get_email_template(trigger: str):
    """Fetch active EmailTemplate by trigger slug. Returns None if not found."""
    try:
        return EmailTemplate.objects.get(trigger=trigger, is_active=True)
    except EmailTemplate.DoesNotExist:
        return None


def send_templated_email(trigger: str, recipient_email: str, context: dict,
                          lead=None, client=None) -> bool:
    """
    Fetch template by trigger, render it, send it, and log result.
    """
    template = _get_email_template(trigger)
    if not template:
        logger.warning(f"[EMAIL] No active template for trigger='{trigger}'")
        return False

    site_name = getattr(settings, 'SITE_NAME', 'NextZen IT Solutions')
    context.setdefault('site_name', site_name)

    subject, body = template.render(context)

    log = EmailLog(
        recipient=recipient_email,
        subject=subject,
        body_html=body,
        template=template,
        lead=lead,
        client=client,
    )

    try:
        mail = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        mail.content_subtype = 'html'
        mail.send(fail_silently=False)
        log.status = 'sent'
        log.save()
        logger.info(f"[EMAIL] Sent '{trigger}' → {recipient_email}")
        return True
    except Exception as e:
        log.status = 'failed'
        log.error  = str(e)
        log.save()
        logger.error(f"[EMAIL] Failed '{trigger}' → {recipient_email}: {e}")
        return False


def send_new_lead_emails(lead) -> None:
    """
    Auto-trigger on new Lead creation:
      1. Welcome email → lead
      2. Admin notification → admin email
    """
    ctx = {
        'name':    lead.name,
        'email':   lead.email,
        'phone':   lead.phone,
        'service': lead.service,
        'budget':  lead.budget,
        'company': lead.company,
        'message': lead.message,
        'source':  lead.get_source_display(),
        'site_url': getattr(settings, 'SITE_URL', ''),
    }

    # Welcome email to lead
    if lead.email:
        send_templated_email('new_lead', lead.email, ctx, lead=lead)

    # Admin notification — send to ALL configured admin emails
    gs = GlobalSettings.get_settings()
    for admin_email in gs.get_admin_notification_emails():
        send_templated_email('admin_notification', admin_email, ctx, lead=lead)


def send_follow_up_emails() -> int:
    """
    Call this from a management command or cron job daily.
    Sends follow-up emails to leads that haven't been contacted yet.
    Returns count of emails sent.
    """
    now   = timezone.now()
    count = 0

    follow_up_map = {
        1: 'follow_up_1',
        3: 'follow_up_3',
        7: 'follow_up_7',
    }

    for days, trigger in follow_up_map.items():
        target_date = (now - timezone.timedelta(days=days)).date()
        leads = Lead.objects.filter(
            status='new',
            created_at__date=target_date,
        ).exclude(
            email_logs__template__trigger=trigger
        )

        for lead in leads:
            if not lead.email:
                continue
            ctx = {
                'name':    lead.name,
                'service': lead.service,
                'budget':  lead.budget,
            }
            sent = send_templated_email(trigger, lead.email, ctx, lead=lead)
            if sent:
                count += 1

    logger.info(f"[FOLLOW-UP] {count} follow-up email(s) sent.")
    return count


# ═══════════════════════════════════════════════════════════════
# ANALYTICS DASHBOARD  (Staff only — /crm/analytics/)
# ═══════════════════════════════════════════════════════════════

@staff_member_required
def analytics_dashboard(request):
    from django.db.models.functions import TruncMonth

    period = request.GET.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    since = timezone.now() - timezone.timedelta(days=days)

    # Lead Metrics
    total_leads      = Lead.objects.count()
    new_leads        = Lead.objects.filter(created_at__gte=since).count()
    converted_leads  = Lead.objects.filter(status='converted').count()
    conversion_rate  = round((converted_leads / total_leads * 100), 1) if total_leads else 0

    # Revenue Metrics
    all_payments    = PaymentOrder.objects.filter(status='paid')
    total_revenue   = all_payments.aggregate(s=Sum('final_amount'))['s'] or 0
    revenue_period  = all_payments.filter(paid_at__gte=since).aggregate(s=Sum('final_amount'))['s'] or 0
    total_orders    = all_payments.count()
    avg_order_value = round(float(total_revenue) / total_orders, 2) if total_orders else 0

    # Lead Source Breakdown
    source_data    = Lead.objects.values('source').annotate(count=Count('id')).order_by('-count')
    source_labels  = [d['source'].replace('_', ' ').title() for d in source_data]
    source_counts  = [d['count'] for d in source_data]

    # Top Services
    top_services = (
        Lead.objects.exclude(service='')
        .values('service')
        .annotate(count=Count('id'))
        .order_by('-count')[:8]
    )

    # Monthly Revenue Chart
    monthly_rev = (
        PaymentOrder.objects.filter(status='paid')
        .annotate(month=TruncMonth('paid_at'))
        .values('month')
        .annotate(total=Sum('final_amount'))
        .order_by('month')
        .filter(month__isnull=False)
    )
    rev_labels = [r['month'].strftime('%b %Y') for r in monthly_rev]
    rev_values = [float(r['total']) for r in monthly_rev]

    # Monthly Lead Chart
    monthly_leads = (
        Lead.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    lead_labels = [l['month'].strftime('%b %Y') for l in monthly_leads]
    lead_counts = [l['count'] for l in monthly_leads]

    # Lead Status Breakdown
    status_data   = Lead.objects.values('status').annotate(count=Count('id'))
    status_labels = [d['status'].title() for d in status_data]
    status_counts = [d['count'] for d in status_data]

    # Top Clients by Revenue
    top_clients = (
        PaymentOrder.objects.filter(status='paid')
        .values('customer_name', 'customer_email')
        .annotate(total=Sum('final_amount'), orders=Count('id'))
        .order_by('-total')[:5]
    )

    # Email Stats
    emails_sent   = EmailLog.objects.filter(status='sent').count()
    emails_failed = EmailLog.objects.filter(status='failed').count()

    context = {
        **base_context(),
        'period':          days,
        'total_leads':     total_leads,
        'new_leads':       new_leads,
        'converted_leads': converted_leads,
        'conversion_rate': conversion_rate,
        'total_revenue':   total_revenue,
        'revenue_period':  revenue_period,
        'total_orders':    total_orders,
        'avg_order_value': avg_order_value,
        'rev_labels':      json.dumps(rev_labels),
        'rev_values':      json.dumps(rev_values),
        'lead_labels':     json.dumps(lead_labels),
        'lead_counts':     json.dumps(lead_counts),
        'source_labels':   json.dumps(source_labels),
        'source_counts':   json.dumps(source_counts),
        'status_labels':   json.dumps(status_labels),
        'status_counts':   json.dumps(status_counts),
        'top_services':    top_services,
        'top_clients':     top_clients,
        'emails_sent':     emails_sent,
        'emails_failed':   emails_failed,
    }

    return render(request, 'website/analytics_dashboard.html', context)




from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import json

from .models import Appointment, BlogPost, BlogCategory, BlogTag, Invoice


# ──────────────────────────────────────────────────────────────
# APPOINTMENT VIEWS
# ──────────────────────────────────────────────────────────────

def appointment_page(request):
    """
    Public booking page. Shows a form to request an appointment.
    GET  → render the booking form
    """
    return render(request, 'website/appointment.html', {
        **base_context(),
        'page_title': 'Book a Free Consultation',
    })


@require_POST
def book_appointment(request):
    """
    Handle appointment booking form submission (AJAX or normal POST).
    Creates an Appointment record with status='pending'.
    Sends a notification email to admin.
    Returns JSON on success or re-renders form on error.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    name         = request.POST.get('name', '').strip()
    email        = request.POST.get('email', '').strip()
    phone        = request.POST.get('phone', '').strip()
    company      = request.POST.get('company', '').strip()
    service      = request.POST.get('service', '').strip()
    message      = request.POST.get('message', '').strip()
    date_str     = request.POST.get('date', '').strip()
    time_str     = request.POST.get('time', '').strip()
    meeting_type = request.POST.get('meeting_type', 'zoom').strip()

    # Basic validation
    errors = {}
    if not name:
        errors['name'] = 'Name is required.'
    if not email:
        errors['email'] = 'Email is required.'
    elif not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        errors['email'] = 'Please enter a valid email address.'
    if not date_str:
        errors['date'] = 'Please select a date.'
    if not time_str:
        errors['time'] = 'Please select a time.'

    if errors:
        if is_ajax:
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        return render(request, 'website/appointment.html', {
            **base_context(),
            'errors': errors, 'form_data': request.POST,
        })

    # Parse date and time
    from datetime import date, time as dtime
    try:
        year, month, day = map(int, date_str.split('-'))
        apt_date = date(year, month, day)
    except (ValueError, AttributeError):
        if is_ajax:
            return JsonResponse({'success': False, 'errors': {'date': 'Invalid date format.'}}, status=400)
        return redirect('appointment')

    try:
        hour, minute = map(int, time_str.split(':'))
        apt_time = dtime(hour, minute)
    except (ValueError, AttributeError):
        if is_ajax:
            return JsonResponse({'success': False, 'errors': {'time': 'Invalid time format.'}}, status=400)
        return redirect('appointment')

    # Create appointment
    appt = Appointment.objects.create(
        name         = name,
        email        = email,
        phone        = phone,
        company      = company,
        service      = service,
        message      = message,
        date         = apt_date,
        time         = apt_time,
        meeting_type = meeting_type,
        status       = 'pending',
    )

    # Auto-link to Lead if email matches
    from .models import Lead
    lead_qs = Lead.objects.filter(email=email).order_by('-created_at')
    if lead_qs.exists():
        appt.lead = lead_qs.first()
        appt.save(update_fields=['lead'])

    # ── Admin ko HTML notification email ────────────────────────────
    try:
        from django.core.mail import EmailMultiAlternatives as _EMA_admin
        from django.template.loader import render_to_string as _rts_admin
        from .models import GlobalSettings as _GS
        _admin_emails = _GS.get_settings().get_admin_notification_emails()
        _admin_url = getattr(settings, 'SITE_URL', '').rstrip('/') + '/admin/bookings/appointmentproxy/'
        _meeting_labels_adm = {
            'zoom': 'Zoom Video Call', 'meet': 'Google Meet',
            'phone': 'Phone Call', 'in_person': 'In Person',
        }
        _meeting_disp_adm = _meeting_labels_adm.get(meeting_type, meeting_type.replace('_',' ').title())
        html_admin = _rts_admin('website/email_appointment_admin.html', {
            'name':       name,
            'email':      email,
            'phone':      phone,
            'company':    company,
            'service':    service,
            'date':       apt_date.strftime('%d %b %Y'),
            'time':       apt_time.strftime('%I:%M %p'),
            'meeting_type': _meeting_disp_adm,
            'message':    message,
            'admin_url':  _admin_url,
            'site_name':  settings.SITE_NAME,
        })
        plain_admin = (
            f'New appointment!\nName: {name}\nEmail: {email}\n'
            f'Date: {apt_date.strftime("%d %b %Y")} {apt_time.strftime("%I:%M %p")}\n'
            f'Meeting: {_meeting_disp_adm}\nMessage: {message}'
        )
        for _ae in _admin_emails:
            msg_adm = _EMA_admin(
                subject    = f'📅 New Appointment — {name} | {apt_date.strftime("%d %b %Y")}',
                body       = plain_admin,
                from_email = settings.DEFAULT_FROM_EMAIL,
                to         = [_ae],
            )
            msg_adm.attach_alternative(html_admin, 'text/html')
            msg_adm.send(fail_silently=True)
    except Exception as _e:
        logger.error(f'[Appointment] Admin email failed: {_e}')

    # ── User ko acknowledgement email (booking received) ─────────────
    try:
        from django.core.mail import EmailMultiAlternatives as _EMA2
        from django.template.loader import render_to_string as _rts2
        from .models import SiteSettings as _SS2

        _ss2           = _SS2.objects.first()
        _support_email = (_ss2.email if _ss2 and _ss2.email else settings.DEFAULT_FROM_EMAIL)
        _site_url      = getattr(settings, 'SITE_URL', '').rstrip('/')
        _meeting_labels = {
            'zoom':      'Zoom Video Call',
            'meet':      'Google Meet',
            'phone':     'Phone Call',
            'in_person': 'In Person',
        }
        _meeting_display = _meeting_labels.get(
            meeting_type,
            meeting_type.replace('_', ' ').title()
        )

        html_body = _rts2('website/email_appointment_confirm.html', {
            'name':          name,
            'email':         email,
            'service':       service or 'General Consultation',
            'date':          apt_date.strftime('%d %b %Y'),
            'time':          apt_time.strftime('%I:%M %p'),
            'meeting_type':  _meeting_display,
            'meeting_link':  None,
            'site_name':     settings.SITE_NAME,
            'site_url':      _site_url,
            'support_email': _support_email,
            'is_confirmed':  False,
        })
        plain_body = (
            f'Dear {name},\n\n'
            f'We received your consultation request.\n\n'
            f'Date    : {apt_date.strftime("%d %b %Y")}\n'
            f'Time    : {apt_time.strftime("%I:%M %p")}\n'
            f'Meeting : {_meeting_display}\n\n'
            f'Our team will confirm your appointment shortly.\n\n'
            f'Regards,\n{settings.SITE_NAME}'
        )
        msg = _EMA2(
            subject    = f'📅 Appointment Request Received — {settings.SITE_NAME}',
            body       = plain_body,
            from_email = settings.DEFAULT_FROM_EMAIL,
            to         = [email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        logger.info(f'[Appointment] ✅ User email sent to {email}')
    except Exception as e:
        logger.error(f'[Appointment] ❌ User email FAILED for {email}: {e}', exc_info=True)

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': 'Your appointment request has been received! We will confirm shortly.',
        })
    return redirect('appointment_confirm')


def appointment_confirm(request):
    """Simple thank-you page after booking."""
    return render(request, 'website/appointment_confirm.html', {
        **base_context(),
        'page_title': 'Appointment Requested!',
    })


# ──────────────────────────────────────────────────────────────
# BLOG VIEWS
# ──────────────────────────────────────────────────────────────

def blog_list(request):
    """
    Public blog listing page.
    Supports ?category=slug and ?tag=slug filters.
    """
    posts      = BlogPost.objects.filter(status='published').select_related('category')
    categories = BlogCategory.objects.filter(is_active=True)
    tags       = BlogTag.objects.all()
    featured   = posts.filter(is_featured=True)[:3]

    # Optional filters
    category_slug = request.GET.get('category')
    tag_slug      = request.GET.get('tag')
    search_query  = request.GET.get('q', '').strip()

    active_category = None
    active_tag      = None

    if category_slug:
        active_category = get_object_or_404(BlogCategory, slug=category_slug, is_active=True)
        posts = posts.filter(category=active_category)

    if tag_slug:
        active_tag = get_object_or_404(BlogTag, slug=tag_slug)
        posts = posts.filter(tags=active_tag)

    if search_query:
        from django.db.models import Q
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination
    from django.core.paginator import Paginator
    paginator  = Paginator(posts, 9)
    page_num   = request.GET.get('page', 1)
    page_obj   = paginator.get_page(page_num)

    return render(request, 'website/blog_list.html', {
        'page_obj'        : page_obj,
        'categories'      : categories,
        'tags'            : tags,
        'featured'        : featured,
        'active_category' : active_category,
        'active_tag'      : active_tag,
        'search_query'    : search_query,
        'page_title'      : 'Blog',
    })


def blog_detail(request, slug):
    """
    Single blog post page.
    Increments view count on each visit.
    """
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    # Increment views atomically to prevent race conditions
    from django.db.models import F
    BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)

    # Related posts (same category, excluding current)
    related = BlogPost.objects.filter(
        status='published', category=post.category
    ).exclude(pk=post.pk).order_by('-published_at')[:3]

    return render(request, 'website/blog_detail.html', {
        'post'       : post,
        'related'    : related,
        # SEO meta tags (used in base template)
        'meta_title'       : post.meta_title or post.title,
        'meta_description' : post.meta_description or post.excerpt,
        'meta_keywords'    : post.meta_keywords,
        'og_image'         : post.og_image.url if post.og_image else (
                             post.cover_image.url if post.cover_image else ''),
    })


def blog_by_category(request, slug):
    """Filter blog posts by category — redirects to blog_list with ?category=."""
    from django.utils.text import slugify
    safe_slug = slugify(slug)  # sanitise slug before using in redirect
    return redirect(f'/blog/?category={safe_slug}')


def blog_by_tag(request, slug):
    """Filter blog posts by tag — redirects to blog_list with ?tag=."""
    from django.utils.text import slugify
    safe_slug = slugify(slug)
    return redirect(f'/blog/?tag={safe_slug}')


# ──────────────────────────────────────────────────────────────
# INVOICE DOWNLOAD VIEW
# ──────────────────────────────────────────────────────────────

def download_invoice(request, invoice_number):
    """
    Serve the invoice PDF for download.
    Can be protected by a token or session check.
    """
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)

    # Generate PDF if it doesn't exist yet
    if not invoice.pdf_file:
        from .invoice_utils import generate_invoice_pdf
        generate_invoice_pdf(invoice, site_name=getattr(settings, 'SITE_NAME', ''))

    response = FileResponse(
        invoice.pdf_file.open('rb'),
        content_type     = 'application/pdf',
        as_attachment    = True,
        filename         = f'{invoice.invoice_number}.pdf',
    )
    return response



# ══════════════════════════════════════════════════════════════════
# INVOICE VIEW ADDITIONS
# ══════════════════════════════════════════════════════════════════



def view_invoice(request, invoice_number):
    """
    Display invoice in browser with beautiful HTML template.
    Used for: viewing invoice before download, email previews.
    """
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    
    # Calculate if invoice is overdue
    from django.utils import timezone
    is_overdue = False
    days_overdue = 0
    
    if invoice.status in ['sent', 'overdue'] and invoice.due_date:
        today = timezone.now().date()
        if invoice.due_date < today:
            is_overdue = True
            days_overdue = (today - invoice.due_date).days
    
    return render(request, 'website/email_invoice.html', {
        'invoice': invoice,
        'is_overdue': is_overdue,
        'days_overdue': days_overdue,
        'site_name': getattr(settings, 'SITE_NAME', 'NextZenDev'),
        'support_email': getattr(settings, 'SUPPORT_EMAIL', invoice.from_email),
        'site_url': getattr(settings, 'SITE_URL', 'https://nextzendev.in'),
    })


def view_payment_invoice(request, invoice_number):
    """
    Display payment confirmation invoice (after successful payment).
    Shows PAID stamp and payment details.
    """
    payment = get_object_or_404(PaymentOrder, invoice_number=invoice_number)
    
    return render(request, 'website/email_invoice.html', {
        'payment': payment,
        'site_name': getattr(settings, 'SITE_NAME', 'NextZenDev'),
        'support_email': getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
        'site_url': getattr(settings, 'SITE_URL', 'https://nextzendev.in'),
    })


@staff_member_required
def send_email_page(request):
    from .models import EmailTemplate, EmailLog
    templates   = EmailTemplate.objects.filter(is_active=True).order_by('name')
    recent_logs = EmailLog.objects.select_related('template').order_by('-sent_at')[:20]
    return render(request, 'website/send_email.html', {
        'templates':   templates,
        'recent_logs': recent_logs,
        'title':       'Send Email',
    })


@staff_member_required
@csrf_exempt
def send_email_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    from .models import EmailTemplate, EmailLog

    to_email       = request.POST.get('to_email', '').strip()
    to_name        = request.POST.get('to_name', '').strip() or 'Valued Customer'
    template_pk    = request.POST.get('template_pk', '').strip()
    custom_subject = request.POST.get('custom_subject', '').strip()

    if not to_email:
        return JsonResponse({'status': 'error', 'message': 'Email address required'})
    if not template_pk:
        return JsonResponse({'status': 'error', 'message': 'Template required'})

    try:
        tmpl = EmailTemplate.objects.get(pk=template_pk, is_active=True)
    except EmailTemplate.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Template not found'})

    context = {
        'name':      to_name,
        'email':     to_email,
        'site_name': getattr(settings, 'SITE_NAME', 'NextZen IT Solutions'),
        'phone': '', 'service': '', 'budget': '', 'company': '', 'message': '',
    }
    subject, body = tmpl.render(context)
    if custom_subject:
        subject = custom_subject

    try:
        mail = EmailMessage(
            subject    = subject,
            body       = body,
            from_email = settings.DEFAULT_FROM_EMAIL,
            to         = [to_email],
        )
        mail.content_subtype = 'html'
        mail.send(fail_silently=False)

        EmailLog.objects.create(
            recipient = to_email,
            subject   = subject,
            body_html = body,
            status    = 'sent',
            template  = tmpl,
        )
        return JsonResponse({'status': 'ok'})

    except Exception as e:
        EmailLog.objects.create(
            recipient = to_email,
            subject   = subject,
            body_html = body,
            status    = 'failed',
            error     = str(e),
            template  = tmpl,
        )
        logger.error(f"[SendEmail] Failed to {to_email}: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})