from django.db import models
import uuid
import secrets
import string


import secrets
import string


def generate_code(length=8):
    """Generate a cryptographically secure short alphanumeric code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, blank=True)
    phone = models.CharField(max_length=15)
    service = models.CharField(max_length=50, blank=True)
    budget = models.CharField(max_length=50, blank=True)
    timeline = models.CharField(max_length=50, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.email or self.phone}"


class Hero(models.Model):
    heading = models.CharField(max_length=200)
    subheading = models.TextField()
    button_text = models.CharField(max_length=50)

    def __str__(self):
        return self.heading


class HeroSection(models.Model):
    heading = models.CharField(max_length=220)
    subheading = models.TextField(blank=True)
    description = models.TextField(blank=True)
    button1_text = models.CharField(max_length=80, blank=True)
    button1_link = models.CharField(max_length=200, blank=True)
    button2_text = models.CharField(max_length=80, blank=True)
    button2_link = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='hero/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.heading

    class Meta:
        ordering = ['order']
        verbose_name = 'Hero Section'
        verbose_name_plural = 'Hero Sections'


class TrustedClient(models.Model):
    name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to='trusted_clients/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Trusted Client'
        verbose_name_plural = 'Trusted Clients'


class WhyChooseUs(models.Model):
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Use emoji or icon class')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
        verbose_name = 'Why Choose Us'
        verbose_name_plural = 'Why Choose Us'


class ProcessStep(models.Model):
    step_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Use emoji or icon class')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.step_number}. {self.title}"

    class Meta:
        ordering = ['step_number']
        verbose_name = 'Process Step'
        verbose_name_plural = 'Process Steps'


class Testimonial(models.Model):
    client_name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)
    company = models.CharField(max_length=120, blank=True)
    feedback = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.client_name

    class Meta:
        ordering = ['order']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'


class Service(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Use emoji or icon class')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'


class Portfolio(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    project_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolio Items'


class SocialMedia(models.Model):
    PLATFORM_CHOICES = [
        ('linkedin',  'LinkedIn'),
        ('instagram', 'Instagram'),
        ('twitter',   'Twitter / X'),
        ('youtube',   'YouTube'),
        ('facebook',  'Facebook'),
        ('whatsapp',  'WhatsApp'),
    ]

    platform  = models.CharField(max_length=20, choices=PLATFORM_CHOICES, unique=True)
    url       = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.get_platform_display()

    class Meta:
        verbose_name = 'Social Media Link'
        verbose_name_plural = 'Social Media Links'


class PricingPlan(models.Model):
    plan_name = models.CharField(max_length=120)
    price = models.CharField(max_length=80)
    features = models.TextField(blank=True, help_text='List each feature on a new line.')
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def feature_list(self):
        return [line.strip() for line in self.features.splitlines() if line.strip()]

    def __str__(self):
        return self.plan_name

    class Meta:
        ordering = ['order']
        verbose_name = 'Pricing Plan'
        verbose_name_plural = 'Pricing Plans'


class FAQ(models.Model):
    question = models.CharField(max_length=220)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'


class ContactLead(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=30)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.email}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Lead'
        verbose_name_plural = 'Contact Leads'


class SiteContent(models.Model):
    PAGE_CHOICES = [
        ('terms', 'Terms & Conditions'),
        ('privacy', 'Privacy Policy'),
        ('refund', 'Refund Policy'),
    ]

    page = models.CharField(max_length=20, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.get_page_display()


class SiteSettings(models.Model):
    site_name        = models.CharField(max_length=100, default="NextZenDev")
    logo             = models.ImageField(upload_to='site/', blank=True, null=True)
    meta_description = models.TextField(
        blank=True,
        help_text='Short description shown in footer brand column and SEO meta tag'
    )
    # ── Emails ──────────────────────────────────────────────────
    email = models.EmailField(
        blank=True,
        help_text='Primary contact email (shown in footer + contact page)',
    )
    contact_emails = models.TextField(
        blank=True,
        help_text=(
            'Additional contact emails shown on the Contact page. '
            'Enter one email per line. Primary email above is always shown first.'
        ),
    )

    # ── Phones ──────────────────────────────────────────────────
    phone = models.CharField(
        max_length=30, blank=True,
        help_text='Primary contact phone (shown in footer + contact page)',
    )
    contact_phones = models.TextField(
        blank=True,
        help_text=(
            'Additional phone numbers shown on the Contact page. '
            'Enter one number per line (e.g. +91 98765 43210). '
            'Primary phone above is always shown first.'
        ),
    )

    # ── WhatsApp ────────────────────────────────────────────────
    whatsapp = models.CharField(
        max_length=30, blank=True, default='',
        help_text='Primary WhatsApp number with country code, no + (e.g. 919155892986)',
    )
    contact_whatsapps = models.TextField(
        blank=True,
        help_text=(
            'Additional WhatsApp numbers shown on the Contact page. '
            'Enter one number per line with country code, no + '
            '(e.g. 919876543210). Primary WhatsApp above is always shown first.'
        ),
    )

    # ── Address ─────────────────────────────────────────────────
    address = models.CharField(max_length=255, blank=True, help_text='Office address shown in footer')

    # ── Helpers ─────────────────────────────────────────────────

    def get_all_contact_emails(self):
        """Returns [primary] + extra emails, deduped. Used in contact page."""
        emails = []
        if self.email:
            emails.append(self.email.strip())
        for line in self.contact_emails.splitlines():
            line = line.strip()
            if line and line not in emails:
                emails.append(line)
        return emails

    def get_all_contact_phones(self):
        """Returns [primary] + extra phones, deduped. Used in contact page."""
        phones = []
        if self.phone:
            phones.append(self.phone.strip())
        for line in self.contact_phones.splitlines():
            line = line.strip()
            if line and line not in phones:
                phones.append(line)
        return phones

    def get_all_whatsapps(self):
        """
        Returns list of dicts: [{'number': '919...', 'display': '+91 915...'}]
        'number' is clean digits for wa.me link, 'display' is the label shown.
        """
        raw_numbers = []
        if self.whatsapp:
            raw_numbers.append(self.whatsapp.strip())
        for line in self.contact_whatsapps.splitlines():
            line = line.strip()
            if line and line not in raw_numbers:
                raw_numbers.append(line)
        result = []
        for num in raw_numbers:
            clean = num.lstrip('+').replace(' ', '').replace('-', '')
            result.append({'number': clean, 'display': f'+{clean}'})
        return result

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'


# ═══════════════════════════════════════════════════════════════
# CHAT MODELS
# ═══════════════════════════════════════════════════════════════

class ChatSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)

    # User details
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)

    # Project details
    project = models.TextField(null=True, blank=True)
    features = models.TextField(null=True, blank=True)
    budget = models.CharField(max_length=100, null=True, blank=True)
    timeline = models.CharField(max_length=100, null=True, blank=True)

    # Flow state
    flow_state = models.CharField(max_length=50, null=True, blank=True)

    # Conversation end tracking
    is_ended   = models.BooleanField(default=False)
    ended_by   = models.CharField(
        max_length=20, null=True, blank=True,
        help_text="'user' or 'admin'"
    )
    ended_at   = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'Unknown'} ({self.session_id[:8]})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20)   # user / bot / admin / system
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"

    class Meta:
        ordering = ['created_at']


# ═══════════════════════════════════════════════════════════════
# COUPON SYSTEM
# ═══════════════════════════════════════════════════════════════

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('flat', 'Flat Amount'),
    ]

    code = models.CharField(max_length=30, unique=True, default=generate_code,
                            help_text='Unique coupon code (auto-generated if blank)')
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percent')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2,
                                         help_text='% or flat ₹ amount')
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          help_text='Minimum order value to apply coupon')
    max_uses = models.PositiveIntegerField(default=0,
                                           help_text='0 = unlimited')
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False, "Coupon is not active."
        if now < self.valid_from:
            return False, "Coupon is not yet valid."
        if now > self.valid_until:
            return False, "Coupon has expired."
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False, "Coupon usage limit reached."
        return True, "Valid"

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == 'percent' else '₹'})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'


class CouponUsage(models.Model):
    """Tracks who used which coupon."""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coupon.code} → {self.email}"

    class Meta:
        ordering = ['-used_at']
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'


# ═══════════════════════════════════════════════════════════════
# REFERRAL SYSTEM
# ═══════════════════════════════════════════════════════════════

class Referral(models.Model):
    """A referral link created by an existing client."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('converted', 'Converted'),
        ('rewarded', 'Rewarded'),
    ]

    # Referrer details
    referrer_name  = models.CharField(max_length=120)
    referrer_email = models.EmailField()
    referrer_phone = models.CharField(max_length=20, blank=True)

    # Unique referral code
    referral_code = models.CharField(max_length=20, unique=True, default=generate_code)

    # Referred person details (filled when they convert)
    referred_name  = models.CharField(max_length=120, blank=True)
    referred_email = models.EmailField(blank=True)
    referred_phone = models.CharField(max_length=20, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Reward: e.g. ₹500 credit, 10% off next project
    reward_description = models.CharField(max_length=200, blank=True,
                                          default='₹500 credit on next project')
    reward_given = models.BooleanField(default=False)

    # ── Admin-controlled fields ──────────────────────────────────
    expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Link expiry date/time. Admin sets this. Blank = never expires.'
    )
    commission_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='₹ commission amount admin approves. Shown in converted email.'
    )
    # ────────────────────────────────────────────────────────────

    created_at   = models.DateTimeField(auto_now_add=True)
    converted_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_expired(self):
        """True if expiry date is set AND has passed."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def referral_link(self):
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
        return f"{site_url}/contact/?ref={self.referral_code}"

    def __str__(self):
        return f"{self.referrer_name} → {self.referral_code} [{self.status}]"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'


# ═══════════════════════════════════════════════════════════════
# AFFILIATE SYSTEM
# ═══════════════════════════════════════════════════════════════

class Affiliate(models.Model):
    """An approved affiliate partner."""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ]

    name    = models.CharField(max_length=150)
    email   = models.EmailField(unique=True)
    phone   = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True, help_text="Affiliate's website/social profile")
    company = models.CharField(max_length=150, blank=True)
    how_promote = models.TextField(blank=True, help_text='How they plan to promote')

    affiliate_code = models.CharField(max_length=20, unique=True, default=generate_code)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00,
                                              help_text='Commission % on converted project value')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    total_clicks    = models.PositiveIntegerField(default=0)
    total_leads     = models.PositiveIntegerField(default=0)
    total_converted = models.PositiveIntegerField(default=0)
    total_earned    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_paid_out  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def pending_payout(self):
        return self.total_earned - self.total_paid_out

    def __str__(self):
        return f"{self.name} ({self.affiliate_code}) — {self.status}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Affiliate'
        verbose_name_plural = 'Affiliates'


class AffiliateClick(models.Model):
    """Tracks every click on an affiliate link."""
    affiliate  = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='clicks')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    landing_page = models.CharField(max_length=300, blank=True)
    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.affiliate.affiliate_code} click at {self.clicked_at}"

    class Meta:
        ordering = ['-clicked_at']
        verbose_name = 'Affiliate Click'
        verbose_name_plural = 'Affiliate Clicks'


class AffiliateConversion(models.Model):
    """Tracks when an affiliate referral converts to a lead/sale."""
    STATUS_CHOICES = [
        ('lead', 'Lead'),
        ('converted', 'Converted to Sale'),
        ('paid', 'Commission Paid'),
    ]

    affiliate   = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='conversions')
    name        = models.CharField(max_length=120)
    email       = models.EmailField()
    phone       = models.CharField(max_length=20, blank=True)
    project     = models.TextField(blank=True)
    order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lead')
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate commission
        if self.order_value and self.affiliate.commission_percent:
            self.commission = (self.order_value * self.affiliate.commission_percent) / 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.affiliate.affiliate_code} → {self.name} [{self.status}]"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Affiliate Conversion'
        verbose_name_plural = 'Affiliate Conversions'



# ═══════════════════════════════════════════════════════════════
# GLOBAL CONTROLS  (add this to the BOTTOM of your models.py)
# ═══════════════════════════════════════════════════════════════

class GlobalSettings(models.Model):
    """
    Singleton model — only ONE row should exist.
    Controls site-wide ON/OFF, maintenance mode, page visibility,
    and section toggles.
    """

    # ── Site ON / OFF ───────────────────────────────────────────
    site_online = models.BooleanField(
        default=True,
        verbose_name='Site Online',
        help_text='Uncheck to put the entire site in maintenance mode.',
    )
    maintenance_title = models.CharField(
        max_length=200,
        default="We'll be back soon!",
        help_text='Heading shown on the maintenance page.',
    )
    maintenance_message = models.TextField(
        default=(
            "We're performing some upgrades to serve you better. "
            "Please check back in a little while."
        ),
        help_text='Body message shown on the maintenance page.',
    )
    maintenance_email = models.EmailField(
        blank=True,
        help_text='Contact email shown on the maintenance page.',
    )
    maintenance_eta = models.CharField(
        max_length=100,
        blank=True,
        help_text='Optional ETA text, e.g. "Back online in ~2 hours".',
    )

    # ── Page toggles ────────────────────────────────────────────
    page_home_active      = models.BooleanField(default=True, verbose_name='Home page')
    page_services_active  = models.BooleanField(default=True, verbose_name='Services page')
    page_portfolio_active = models.BooleanField(default=True, verbose_name='Portfolio page')
    page_about_active     = models.BooleanField(default=True, verbose_name='About page')
    page_contact_active   = models.BooleanField(default=True, verbose_name='Contact page')
    page_coupons_active   = models.BooleanField(default=True, verbose_name='Coupons page')
    page_referral_active  = models.BooleanField(default=True, verbose_name='Referral page')
    page_affiliate_active = models.BooleanField(default=True, verbose_name='Affiliate page')
    page_blog_active      = models.BooleanField(default=True, verbose_name='Blog page')

    # ── Section toggles (home page) ─────────────────────────────
    section_hero_active         = models.BooleanField(default=True, verbose_name='Hero section')
    section_trusted_active      = models.BooleanField(default=True, verbose_name='Trusted clients section')
    section_services_active     = models.BooleanField(default=True, verbose_name='Services section')
    section_why_choose_active   = models.BooleanField(default=True, verbose_name='Why choose us section')
    section_process_active      = models.BooleanField(default=True, verbose_name='Process steps section')
    section_portfolio_active    = models.BooleanField(default=True, verbose_name='Portfolio section')
    section_testimonials_active = models.BooleanField(default=True, verbose_name='Testimonials section')
    section_pricing_active      = models.BooleanField(default=True, verbose_name='Pricing section')
    section_faq_active          = models.BooleanField(default=True, verbose_name='FAQ section')
    section_contact_active      = models.BooleanField(default=True, verbose_name='Contact form section')
    section_chatbot_active      = models.BooleanField(default=True, verbose_name='Chatbot widget')

    # ── Feature toggles ─────────────────────────────────────────
    feature_coupons_active   = models.BooleanField(default=True, verbose_name='Coupon system')
    feature_referral_active  = models.BooleanField(default=True, verbose_name='Referral system')
    feature_affiliate_active = models.BooleanField(default=True, verbose_name='Affiliate system')
    feature_ai_chat_active   = models.BooleanField(default=True, verbose_name='AI chatbot')

    # ── Admin Notification Emails ───────────────────────────────
    admin_notification_emails = models.TextField(
        blank=True,
        help_text=(
            'Comma-separated email addresses that receive admin alerts '
            '(new leads, contact form submissions, appointments). '
            'If empty, falls back to DEFAULT_FROM_EMAIL from settings. '
            'Example: owner@example.com, sales@example.com'
        ),
    )

    # ── Bypass IPs (comma-separated) ────────────────────────────
    bypass_ips = models.TextField(
        blank=True,
        help_text='Comma-separated IP addresses that can bypass maintenance mode (e.g. your office IP).',
    )

    updated_at = models.DateTimeField(auto_now=True)

    def get_admin_notification_emails(self):
        """
        Returns a list of admin emails that should receive notification alerts.
        Falls back to settings.DEFAULT_FROM_EMAIL if the field is empty.
        """
        from django.conf import settings as django_settings
        emails = [e.strip() for e in self.admin_notification_emails.split(',') if e.strip()]
        if not emails:
            fallback = getattr(django_settings, 'DEFAULT_FROM_EMAIL', '')
            if fallback:
                emails = [fallback]
        return emails

    def get_bypass_ips(self):
        """Return list of whitelisted IPs."""
        return [ip.strip() for ip in self.bypass_ips.split(',') if ip.strip()]

    @classmethod
    def get_settings(cls):
        """Always returns the singleton row, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        status = "🟢 Online" if self.site_online else "🔴 Maintenance"
        return f"Global Settings — {status}"

    class Meta:
        verbose_name = 'Global Settings'
        verbose_name_plural = 'Global Settings'



# ═══════════════════════════════════════════════════════════════
# LEAD CRM
# ═══════════════════════════════════════════════════════════════

class Lead(models.Model):
    """Full CRM lead pipeline with team assignment and notes."""

    STATUS_CHOICES = [
        ('new',        '🆕 New'),
        ('contacted',  '📞 Contacted'),
        ('converted',  '✅ Converted'),
        ('rejected',   '❌ Rejected'),
    ]

    SOURCE_CHOICES = [
        ('contact_form', 'Contact Form'),
        ('chatbot',      'Chatbot'),
        ('referral',     'Referral'),
        ('affiliate',    'Affiliate'),
        ('manual',       'Manual Entry'),
        ('other',        'Other'),
    ]

    # ── Core Info ───────────────────────────────────────────────
    name    = models.CharField(max_length=150)
    email   = models.EmailField(blank=True)
    phone   = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=150, blank=True)

    # ── Project Details ─────────────────────────────────────────
    service   = models.CharField(max_length=150, blank=True)
    budget    = models.CharField(max_length=100, blank=True)
    timeline  = models.CharField(max_length=100, blank=True)
    message   = models.TextField(blank=True)

    # ── Pipeline ────────────────────────────────────────────────
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')

    # ── Team Assignment ─────────────────────────────────────────
    assigned_to = models.CharField(
        max_length=150, blank=True,
        help_text='Team member name or email responsible for this lead'
    )

    # ── Notes ───────────────────────────────────────────────────
    notes = models.TextField(blank=True, help_text='Internal notes visible only to team')

    # ── Tracking ────────────────────────────────────────────────
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    contacted_at  = models.DateTimeField(null=True, blank=True)
    converted_at  = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} — {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'


class LeadNote(models.Model):
    """Timeline of notes/activity against a lead."""
    lead      = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='lead_notes')
    author    = models.CharField(max_length=150, blank=True)
    note      = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note on {self.lead.name} @ {self.created_at:%d %b %Y}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead Note'
        verbose_name_plural = 'Lead Notes'


# ═══════════════════════════════════════════════════════════════
# PAYMENT SYSTEM
# ═══════════════════════════════════════════════════════════════

class PaymentOrder(models.Model):
    """
    Created when a customer initiates a payment from the website.
    Stores Razorpay order details and final status.
    """

    STATUS_CHOICES = [
        ('pending',  '⏳ Pending'),
        ('paid',     '✅ Paid'),
        ('failed',   '❌ Failed'),
        ('refunded', '↩️ Refunded'),
    ]

    # ── Customer ────────────────────────────────────────────────
    customer_name  = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30, blank=True)

    # ── Order Details ───────────────────────────────────────────
    description    = models.CharField(max_length=300, blank=True, help_text='What the payment is for')
    amount         = models.DecimalField(max_digits=12, decimal_places=2, help_text='Amount in INR')
    coupon         = models.ForeignKey(
        'Coupon', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='payments'
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount    = models.DecimalField(max_digits=12, decimal_places=2, help_text='Amount charged after discount')

    # ── Razorpay ────────────────────────────────────────────────
    razorpay_order_id   = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature  = models.CharField(max_length=300, blank=True)

    # ── Invoice ─────────────────────────────────────────────────
    invoice_number  = models.CharField(max_length=30, blank=True, unique=True)
    invoice_sent    = models.BooleanField(default=False)

    # ── Status & Timestamps ─────────────────────────────────────
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at    = models.DateTimeField(null=True, blank=True)

    # ── Link to Lead ────────────────────────────────────────────
    lead = models.ForeignKey(
        Lead, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='payments',
        help_text='Auto-linked lead from CRM'
    )

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            from django.db import transaction
            with transaction.atomic():
                year  = timezone.now().year
                count = PaymentOrder.objects.select_for_update().filter(
                    created_at__year=year
                ).count() + 1
                self.invoice_number = f"INV-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} — {self.customer_name} ₹{self.final_amount} [{self.status}]"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Order'
        verbose_name_plural = 'Payment Orders'


# ──────────────────────────────────────────────────────────────
# NEWSLETTER SUBSCRIBER
# ──────────────────────────────────────────────────────────────

class NewsletterSubscriber(models.Model):
    email      = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.email} ({'active' if self.is_active else 'unsubscribed'})"

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'

# ═══════════════════════════════════════════════════════════════
# PAYMENT OTP VERIFICATION
# ═══════════════════════════════════════════════════════════════

class PaymentOTP(models.Model):
    """
    Stores email + phone OTP for payment verification.
    One row per (email, session). Expires in 5 minutes.

    Security:
      - email_otp / phone_otp stores SHA-256 HASH (64 chars), never plain text
      - attempts  : max 5 wrong tries → record deleted (brute force protection)
      - resend_count : max 3 resends per session (rate limiting)
      - Record deleted immediately after successful verification (one-time use)
    """

    email          = models.EmailField()
    phone          = models.CharField(max_length=30, blank=True)

    # SHA-256 hash = 64 hex chars — plain OTP never stored
    email_otp      = models.CharField(max_length=64)
    phone_otp      = models.CharField(max_length=64, blank=True)

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    attempts       = models.PositiveSmallIntegerField(default=0)   # max 5
    resend_count   = models.PositiveSmallIntegerField(default=0)   # max 3  ← NEW

    created_at     = models.DateTimeField(auto_now_add=True)
    expires_at     = models.DateTimeField()

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def is_verified(self):
        """Either email OR phone verified is enough."""
        return self.email_verified or self.phone_verified

    def __str__(self):
        return f"OTP for {self.email} | email={'✅' if self.email_verified else '❌'} phone={'✅' if self.phone_verified else '❌'}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment OTP'
        verbose_name_plural = 'Payment OTPs'




# ═══════════════════════════════════════════════════════════════
# ENHANCED CRM — models.py ke BOTTOM mein paste karo (PaymentOTP ke baad)
# ═══════════════════════════════════════════════════════════════

from django.db import models
from django.utils import timezone


# ───────────────────────────────────────────────
# CLIENT  (Lead se convert hone ke baad)
# ───────────────────────────────────────────────

class Client(models.Model):
    """A converted lead becomes a Client."""

    # Link to original lead (optional)
    lead = models.OneToOneField(
        'Lead', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='client_profile'
    )

    # Basic info
    name    = models.CharField(max_length=150)
    email   = models.EmailField()
    phone   = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True)

    # Business info
    gstin   = models.CharField(max_length=15, blank=True, help_text='GST number if applicable')
    website = models.URLField(blank=True)

    # Lifetime value tracking
    total_revenue    = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                           help_text='Auto-updated from payments')
    project_count    = models.PositiveIntegerField(default=0)
    is_active        = models.BooleanField(default=True)

    # Notes
    internal_notes   = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_lifetime_value(self):
        """Recalculate total revenue from all paid PaymentOrders for this client."""
        from django.db.models import Sum
        total = PaymentOrder.objects.filter(
            customer_email=self.email, status='paid'
        ).aggregate(s=Sum('final_amount'))['s'] or 0
        self.total_revenue  = total
        self.project_count  = self.projects.count()
        self.save(update_fields=['total_revenue', 'project_count'])

    def __str__(self):
        return f"{self.name} — {self.company or self.email}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'


# ───────────────────────────────────────────────
# PROJECT
# ───────────────────────────────────────────────

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning',    '📋 Planning'),
        ('in_progress', '🔧 In Progress'),
        ('review',      '👀 Under Review'),
        ('completed',   '✅ Completed'),
        ('on_hold',     '⏸️ On Hold'),
        ('cancelled',   '❌ Cancelled'),
    ]

    client      = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    service     = models.CharField(max_length=150, blank=True)

    # Financials
    budget       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Progress (0-100)
    progress     = models.PositiveIntegerField(default=0, help_text='0–100 percent complete')

    # Status & Timeline
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date   = models.DateField(null=True, blank=True)
    deadline     = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Team
    assigned_to  = models.CharField(max_length=150, blank=True)

    # Linked payment
    payment = models.ForeignKey(
        'PaymentOrder', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='projects'
    )

    internal_notes = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def is_overdue(self):
        if self.deadline and self.status not in ('completed', 'cancelled'):
            return timezone.now().date() > self.deadline
        return False

    def __str__(self):
        return f"{self.title} [{self.client.name}] — {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


# ───────────────────────────────────────────────
# COMMUNICATION LOG
# ───────────────────────────────────────────────

class CommunicationLog(models.Model):
    TYPE_CHOICES = [
        ('email',   '📧 Email'),
        ('phone',   '📞 Phone Call'),
        ('meeting', '🤝 Meeting'),
        ('whatsapp','💬 WhatsApp'),
        ('other',   '📝 Other'),
    ]

    client   = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='communications')
    project  = models.ForeignKey(Project, null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name='communications')

    comm_type  = models.CharField(max_length=20, choices=TYPE_CHOICES, default='email')
    subject    = models.CharField(max_length=250)
    summary    = models.TextField(help_text='What was discussed / communicated')

    # Who did it
    done_by    = models.CharField(max_length=150, blank=True, help_text='Team member name')

    comm_date  = models.DateTimeField(default=timezone.now)
    follow_up_date = models.DateField(null=True, blank=True,
                                      help_text='Set if a follow-up is needed')
    follow_up_done = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_comm_type_display()} — {self.subject[:50]} ({self.client.name})"

    class Meta:
        ordering = ['-comm_date']
        verbose_name = 'Communication Log'
        verbose_name_plural = 'Communication Logs'


# ───────────────────────────────────────────────
# TASK MANAGEMENT
# ───────────────────────────────────────────────

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low',    '🟢 Low'),
        ('medium', '🟡 Medium'),
        ('high',   '🔴 High'),
        ('urgent', '🚨 Urgent'),
    ]
    STATUS_CHOICES = [
        ('todo',        '📋 To Do'),
        ('in_progress', '🔧 In Progress'),
        ('done',        '✅ Done'),
        ('cancelled',   '❌ Cancelled'),
    ]

    project     = models.ForeignKey(Project, null=True, blank=True,
                                     on_delete=models.CASCADE, related_name='tasks')
    client      = models.ForeignKey(Client, null=True, blank=True,
                                     on_delete=models.CASCADE, related_name='tasks')
    lead        = models.ForeignKey('Lead', null=True, blank=True,
                                     on_delete=models.CASCADE, related_name='tasks')

    title       = models.CharField(max_length=250)
    description = models.TextField(blank=True)

    assigned_to = models.CharField(max_length=150, blank=True)
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')

    due_date    = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def is_overdue(self):
        return (self.due_date and self.status not in ('done', 'cancelled')
                and timezone.now().date() > self.due_date)

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title} — {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


# ───────────────────────────────────────────────
# EMAIL TEMPLATE
# ───────────────────────────────────────────────

class EmailTemplate(models.Model):
    TRIGGER_CHOICES = [
        ('new_lead',          '🆕 New Lead (auto)'),
        ('admin_notification', '🔔 Admin Notification (auto)'),
        ('welcome_client',    '👋 Welcome Client (auto)'),
        ('follow_up_1',       '📅 Follow-up Day 1 (auto)'),
        ('follow_up_3',       '📅 Follow-up Day 3 (auto)'),
        ('follow_up_7',       '📅 Follow-up Day 7 (auto)'),
        ('custom',            '✉️ Custom / Manual'),
    ]

    name        = models.CharField(max_length=100, unique=True,
                                   help_text='Internal name, e.g. "New Lead Welcome"')
    trigger     = models.CharField(max_length=30, choices=TRIGGER_CHOICES, default='custom')
    subject     = models.CharField(max_length=250,
                                   help_text='Use {{name}}, {{service}}, {{company}} as placeholders')
    body_html   = models.TextField(
        help_text='HTML body. Placeholders: {{name}}, {{email}}, {{phone}}, {{service}}, {{budget}}, {{company}}, {{site_name}}'
    )
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def render(self, context: dict) -> tuple[str, str]:
        """Return (subject, body) with placeholders replaced."""
        subject = self.subject
        body    = self.body_html
        for key, val in context.items():
            placeholder = '{{' + key + '}}'
            subject = subject.replace(placeholder, str(val))
            body    = body.replace(placeholder, str(val))
        return subject, body

    def __str__(self):
        return f"{self.name} [{self.get_trigger_display()}]"

    class Meta:
        ordering = ['trigger', 'name']
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'


# ───────────────────────────────────────────────
# EMAIL LOG  (har sent email ka record)
# ───────────────────────────────────────────────

class EmailLog(models.Model):
    STATUS_CHOICES = [
        ('sent',   '✅ Sent'),
        ('failed', '❌ Failed'),
    ]

    recipient   = models.EmailField()
    subject     = models.CharField(max_length=250)
    body_html   = models.TextField(blank=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    error       = models.TextField(blank=True, help_text='Error message if failed')
    template    = models.ForeignKey(EmailTemplate, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='logs')

    # Optional links
    lead        = models.ForeignKey('Lead', null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='email_logs')
    client      = models.ForeignKey(Client, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='email_logs')

    sent_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.status} → {self.recipient} | {self.subject[:40]}"

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'



# ═══════════════════════════════════════════════════════════════
# PASTE THIS AT THE BOTTOM OF YOUR EXISTING models.py
# ═══════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────
# APPOINTMENT SYSTEM
# ───────────────────────────────────────────────────────────────

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending',   '⏳ Pending'),
        ('confirmed', '✅ Confirmed'),
        ('cancelled', '❌ Cancelled'),
        ('completed', '🎉 Completed'),
        ('no_show',   '👻 No Show'),
    ]
    MEETING_TYPE_CHOICES = [
        ('zoom',    '🎥 Zoom'),
        ('meet',    '📹 Google Meet'),
        ('phone',   '📞 Phone Call'),
        ('in_person', '🤝 In Person'),
    ]

    # ── Client Info ─────────────────────────────────────────────
    name    = models.CharField(max_length=150)
    email   = models.EmailField()
    phone   = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=150, blank=True)

    # ── Appointment Details ─────────────────────────────────────
    service     = models.CharField(max_length=150, blank=True,
                                   help_text='What they want to discuss')
    message     = models.TextField(blank=True, help_text='Any specific requirements')
    date        = models.DateField()
    time        = models.TimeField()
    duration    = models.PositiveIntegerField(default=30,
                                              help_text='Duration in minutes')

    # ── Meeting ─────────────────────────────────────────────────
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES,
                                    default='zoom')
    meeting_link = models.URLField(blank=True,
                                   help_text='Zoom / Meet link (auto or manual)')

    # ── Status & Assignment ─────────────────────────────────────
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                   default='pending')
    assigned_to = models.CharField(max_length=150, blank=True,
                                   help_text='Team member handling this call')

    # ── CRM Links ───────────────────────────────────────────────
    lead   = models.ForeignKey('Lead', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='appointments')
    client = models.ForeignKey('Client', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='appointments')

    # ── Confirmation & Reminders ────────────────────────────────
    confirmation_sent = models.BooleanField(default=False)
    reminder_sent     = models.BooleanField(default=False)
    internal_notes    = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} — {self.date} {self.time} [{self.get_status_display()}]"

    class Meta:
        ordering = ['-date', '-time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'


# ─────────────────────────────────────────────────────────────
# BLOG / SEO SYSTEM
# ─────────────────────────────────────────────────────────────

class BlogCategory(models.Model):
    name    = models.CharField(max_length=100, unique=True)
    slug    = models.SlugField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'


class BlogTag(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Blog Tag'
        verbose_name_plural = 'Blog Tags'


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft',     '✏️ Draft'),
        ('published', '✅ Published'),
        ('archived',  '📦 Archived'),
    ]

    # ── Content ─────────────────────────────────────────────────
    title       = models.CharField(max_length=220)
    slug        = models.SlugField(max_length=250, unique=True,
                                   help_text='Auto-generated from title if left blank')
    excerpt     = models.TextField(max_length=400, blank=True,
                                   help_text='Short summary shown in listings')
    content     = models.TextField(help_text='Full HTML / Markdown content')
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True)

    # ── Taxonomy ────────────────────────────────────────────────
    category = models.ForeignKey(BlogCategory, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name='posts')
    tags     = models.ManyToManyField(BlogTag, blank=True, related_name='posts')

    # ── SEO ─────────────────────────────────────────────────────
    meta_title       = models.CharField(max_length=70, blank=True,
                                        help_text='SEO title (max 60 chars recommended)')
    meta_description = models.CharField(max_length=170, blank=True,
                                        help_text='SEO description (max 160 chars)')
    meta_keywords    = models.CharField(max_length=300, blank=True,
                                        help_text='Comma-separated keywords')
    canonical_url    = models.URLField(blank=True,
                                       help_text='Leave blank to auto-generate')
    og_image         = models.ImageField(upload_to='blog/og/', blank=True, null=True,
                                         help_text='Open Graph image for social sharing')

    # ── Publishing ──────────────────────────────────────────────
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                    default='draft')
    author       = models.CharField(max_length=100, default='NextZen Team')
    published_at = models.DateTimeField(null=True, blank=True)

    # ── Stats ───────────────────────────────────────────────────
    views        = models.PositiveIntegerField(default=0, editable=False)
    is_featured  = models.BooleanField(default=False,
                                       help_text='Show in featured/highlighted section')

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        if not self.meta_title:
            self.meta_title = self.title[:70]
        if not self.excerpt and self.content:
            # Strip HTML tags for auto-excerpt
            import re
            clean = re.sub('<[^>]+>', '', self.content)
            self.excerpt = clean[:300]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'


# ─────────────────────────────────────────────────────────────
# INVOICE SYSTEM
# ─────────────────────────────────────────────────────────────

class InvoiceItem(models.Model):
    """Line items for an invoice."""
    invoice     = models.ForeignKey('Invoice', on_delete=models.CASCADE,
                                    related_name='items')
    description = models.CharField(max_length=250)
    quantity    = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} × {self.quantity}"

    class Meta:
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft',    '✏️ Draft'),
        ('sent',     '📧 Sent'),
        ('paid',     '✅ Paid'),
        ('overdue',  '⚠️ Overdue'),
        ('cancelled','❌ Cancelled'),
    ]

    # ── Invoice Number ──────────────────────────────────────────
    invoice_number = models.CharField(max_length=30, unique=True, blank=True)

    # ── Client / Billing Info ───────────────────────────────────
    client        = models.ForeignKey('Client', null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='invoices')
    client_name   = models.CharField(max_length=150, help_text='Billed to name')
    client_email  = models.EmailField()
    client_phone  = models.CharField(max_length=30, blank=True)
    client_address= models.TextField(blank=True)
    client_gstin  = models.CharField(max_length=15, blank=True)
    client_company= models.CharField(max_length=150, blank=True)

    # ── Your Company ────────────────────────────────────────────
    from_name     = models.CharField(max_length=150, default='NextZen IT Solutions')
    from_email    = models.EmailField(default='connect@nextzendev.in')
    from_address  = models.TextField(blank=True)
    from_gstin    = models.CharField(max_length=15, blank=True)

    # ── Dates ───────────────────────────────────────────────────
    issue_date    = models.DateField(default=timezone.now)
    due_date      = models.DateField(null=True, blank=True)

    # ── Financials ──────────────────────────────────────────────
    subtotal      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_percent   = models.DecimalField(max_digits=5, decimal_places=2, default=18,
                                        help_text='GST % (e.g. 18)')
    tax_amount    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount  = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # ── Coupon / Payment Links ──────────────────────────────────
    payment_order = models.ForeignKey('PaymentOrder', null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='invoices')

    # ── Notes ───────────────────────────────────────────────────
    notes         = models.TextField(blank=True,
                                     help_text='Bank details, thank you note, terms etc.')
    terms         = models.TextField(blank=True,
                                     help_text='Payment terms, e.g. "Due within 7 days"')

    # ── Status ──────────────────────────────────────────────────
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                     default='draft')
    sent_at       = models.DateTimeField(null=True, blank=True)
    paid_at       = models.DateTimeField(null=True, blank=True)
    pdf_file      = models.FileField(upload_to='invoices/', blank=True, null=True,
                                     help_text='Auto-generated PDF stored here')

    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def recalculate(self):
        """Recalculate subtotal, tax, and total from line items."""
        from django.db.models import Sum, F, ExpressionWrapper, DecimalField as DF
        subtotal = sum(item.total for item in self.items.all())
        tax      = (subtotal * self.tax_percent) / 100
        total    = subtotal + tax - self.discount
        self.subtotal     = subtotal
        self.tax_amount   = tax
        self.total_amount = total
        self.save(update_fields=['subtotal', 'tax_amount', 'total_amount'])

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.db import transaction
            with transaction.atomic():
                year  = timezone.now().year
                count = Invoice.objects.select_for_update().filter(
                    created_at__year=year
                ).count() + 1
                self.invoice_number = f"NZ-INV-{year}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} — {self.client_name} ₹{self.total_amount} [{self.status}]"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'


# ══════════════════════════════════════════════════════════════════
# models_jazzmin_groups.py
#
# Ye file tumhari existing models.py ke NEECHE paste karo
# (class InvoiceItem aur class Invoice ke baad, file ke bilkul end mein)
#
# Kya karta hai: Proxy models banata hai jo django-jazzmin ke
# sidebar mein alag sections mein group ho jaate hain.
# Koi database change nahi hota — sirf admin grouping change hoti hai.
# ══════════════════════════════════════════════════════════════════

# ── Proxy models for sidebar grouping ─────────────────────────────
# Har group ke liye ek alag app_label assign kiya hai.
# Jazzmin inhe alag sections ki tarah treat karta hai.

# NOTE: Ye proxy models tumhari models.py ke end mein paste karo.
# Migration banana hoga: python manage.py makemigrations && migrate


# ─── Group: crm ────────────────────────────────────────────────────

class ClientProxy(Client):
    class Meta:
        proxy        = True
        app_label    = 'crm'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'


class ProjectProxy(Project):
    class Meta:
        proxy        = True
        app_label    = 'crm'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


class CommunicationLogProxy(CommunicationLog):
    class Meta:
        proxy        = True
        app_label    = 'crm'
        verbose_name = 'Communication Log'
        verbose_name_plural = 'Communication Logs'


class TaskProxy(Task):
    class Meta:
        proxy        = True
        app_label    = 'crm'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class LeadProxy(Lead):
    class Meta:
        proxy        = True
        app_label    = 'crm'
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'


# ─── Group: payments ───────────────────────────────────────────────

class PaymentOrderProxy(PaymentOrder):
    class Meta:
        proxy        = True
        app_label    = 'payments'
        verbose_name = 'Payment Order'
        verbose_name_plural = 'Payment Orders'


class InvoiceProxy(Invoice):
    class Meta:
        proxy        = True
        app_label    = 'payments'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'


# ─── Group: chat_app ───────────────────────────────────────────────

class ChatSessionProxy(ChatSession):
    class Meta:
        proxy        = True
        app_label    = 'chat_app'
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'


class ChatMessageProxy(ChatMessage):
    class Meta:
        proxy        = True
        app_label    = 'chat_app'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'


# ─── Group: blog_app ───────────────────────────────────────────────

class BlogPostProxy(BlogPost):
    class Meta:
        proxy        = True
        app_label    = 'blog_app'
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'


class BlogCategoryProxy(BlogCategory):
    class Meta:
        proxy        = True
        app_label    = 'blog_app'
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'


class BlogTagProxy(BlogTag):
    class Meta:
        proxy        = True
        app_label    = 'blog_app'
        verbose_name = 'Blog Tag'
        verbose_name_plural = 'Blog Tags'


# ─── Group: growth ─────────────────────────────────────────────────

class CouponProxy(Coupon):
    class Meta:
        proxy        = True
        app_label    = 'growth'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'


class CouponUsageProxy(CouponUsage):
    class Meta:
        proxy        = True
        app_label    = 'growth'
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'


class ReferralProxy(Referral):
    class Meta:
        proxy        = True
        app_label    = 'growth'
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'


class AffiliateProxy(Affiliate):
    class Meta:
        proxy        = True
        app_label    = 'growth'
        verbose_name = 'Affiliate'
        verbose_name_plural = 'Affiliates'


class AffiliateConversionProxy(AffiliateConversion):
    class Meta:
        proxy        = True
        app_label    = 'growth'
        verbose_name = 'Affiliate Conversion'
        verbose_name_plural = 'Affiliate Conversions'


# ─── Group: email_app ──────────────────────────────────────────────

class EmailTemplateProxy(EmailTemplate):
    class Meta:
        proxy        = True
        app_label    = 'email_app'
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'


class EmailLogProxy(EmailLog):
    class Meta:
        proxy        = True
        app_label    = 'email_app'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'


class NewsletterSubscriberProxy(NewsletterSubscriber):
    class Meta:
        proxy        = True
        app_label    = 'email_app'
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'


# ─── Group: bookings ───────────────────────────────────────────────

class AppointmentProxy(Appointment):
    class Meta:
        proxy        = True
        app_label    = 'bookings'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'


# ─── Group: contacts ───────────────────────────────────────────────

class ContactProxy(Contact):
    class Meta:
        proxy        = True
        app_label    = 'contacts'
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'


class ContactLeadProxy(ContactLead):
    class Meta:
        proxy        = True
        app_label    = 'contacts'
        verbose_name = 'Contact Lead'
        verbose_name_plural = 'Contact Leads'