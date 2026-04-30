"""
signals.py — NextZen IT Solutions
=====================================
Referral + Affiliate automation engine.

Kya karta hai:
  • Referral convert hone par referrer ko email + reward_given=True auto-set
  • Affiliate status 'active' hone par affiliate ko approval email
  • AffiliateConversion 'converted' hone par:
      - Commission auto-calculate (model.save() mein already hai)
      - Affiliate.total_earned + total_converted update
      - Affiliate ko commission email
  • AffiliateConversion 'paid' hone par:
      - Affiliate.total_paid_out update

Setup (karo ek baar):
  1. Apni app ki apps.py mein ready() mein import karo:
       from . import signals  # noqa
  2. Ya seedha website/apps.py mein:
       class WebsiteConfig(AppConfig):
           ...
           def ready(self):
               import website.signals  # noqa
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# ── lazy imports to avoid circular imports ──────────────────────
def _get_models():
    from .models import Referral, Affiliate, AffiliateConversion, SiteSettings
    return Referral, Affiliate, AffiliateConversion, SiteSettings


def _site_name():
    try:
        from .models import SiteSettings
        ss = SiteSettings.objects.first()
        return ss.site_name if ss else getattr(settings, 'SITE_NAME', 'NextZenDev')
    except Exception:
        return getattr(settings, 'SITE_NAME', 'NextZenDev')


def _support_email():
    try:
        from .models import SiteSettings
        ss = SiteSettings.objects.first()
        return ss.email if (ss and ss.email) else settings.DEFAULT_FROM_EMAIL
    except Exception:
        return settings.DEFAULT_FROM_EMAIL


def _send_html_email(subject, to_email, html_body, plain_body=None):
    """Helper — sends HTML email, never raises."""
    try:
        plain = plain_body or 'Please view this email in an HTML-compatible client.'
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=True)
        logger.info(f'[Signal Email] Sent "{subject}" to {to_email}')
    except Exception as e:
        logger.error(f'[Signal Email] Failed to send "{subject}" to {to_email}: {e}')


# ══════════════════════════════════════════════════════════════════
# REFERRAL SIGNALS
# ══════════════════════════════════════════════════════════════════

# Track previous Referral status to detect changes (same pattern as Affiliate)
_referral_prev_status = {}


@receiver(pre_save, sender='website.Referral')
def referral_pre_save(sender, instance, **kwargs):
    """Save previous status before save so post_save can detect changes."""
    if instance.pk:
        try:
            from .models import Referral
            old = Referral.objects.get(pk=instance.pk)
            _referral_prev_status[instance.pk] = old.status
        except Exception:
            pass


@receiver(post_save, sender='website.Referral')
def on_referral_save(sender, instance, created, **kwargs):
    """
    Trigger:  Referral object save hone par
    Actions:
      • Naya referral bana  → referrer ko 'link ready' email (NO reward details)
      • status → 'converted' → referrer ko email: "Aapka referral convert hua, ₹X milega"
      • status → 'rewarded'  → referrer ko email: "Aapka ₹X commission/reward process ho gaya"
    """
    Referral, Affiliate, AffiliateConversion, SiteSettings = _get_models()
    site     = _site_name()
    support  = _support_email()
    site_url = getattr(settings, 'SITE_URL', '')

    prev_status = _referral_prev_status.pop(instance.pk, None)

    # ── Case 1: Naya referral create hua ────────────────────────
    if created:
        ref_link = f"{site_url}/contact/?ref={instance.referral_code}"
        subject  = f"🎉 Your referral link is ready — {site}"
        html     = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f9fafb;border-radius:12px;">
          <h2 style="color:#0f172a;">Hi {instance.referrer_name}! 👋</h2>
          <p style="color:#475569;">Your referral link is ready. Share it with friends who need IT solutions — you earn a reward for every successful referral!</p>

          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin:24px 0;">
            <p style="font-size:12px;color:#94a3b8;margin:0 0 8px;text-transform:uppercase;letter-spacing:.05em;">Your referral link</p>
            <p style="font-family:monospace;color:#6366f1;font-size:14px;word-break:break-all;margin:0;">
              <a href="{ref_link}" style="color:#6366f1;">{ref_link}</a>
            </p>
            <p style="font-size:12px;color:#94a3b8;margin:8px 0 0;">Code: <strong>{instance.referral_code}</strong></p>
          </div>

          <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin:24px 0;">
            <p style="color:#15803d;font-weight:600;margin:0 0 6px;">🎁 Your reward</p>
            <p style="color:#166534;margin:0;">{instance.reward_description or '₹500 credit on your next project'}</p>
          </div>

          <p style="color:#475569;font-size:14px;">Questions? Reply to this email or contact us at <a href="mailto:{support}">{support}</a></p>
          <p style="color:#94a3b8;font-size:12px;margin-top:32px;">— The {site} Team</p>
        </div>
        """
        plain = (
            f"Hi {instance.referrer_name},\n\n"
            f"Your referral link is ready!\n\n"
            f"Link: {ref_link}\n"
            f"Code: {instance.referral_code}\n\n"
            f"Reward: {instance.reward_description or '₹500 credit on your next project'}\n\n"
            f"— {site}"
        )
        _send_html_email(subject, instance.referrer_email, html, plain)
        return

    # ── Case 2: Status changed to 'converted' ───────────────────
    # Send TWO emails:
    #   a) Referrer: "Your referral converted — you'll earn ₹X (pending approval)"
    #   b) Admin: "Referral converted — action required"
    if prev_status and prev_status != 'converted' and instance.status == 'converted':

        # (a) Email to referrer ──────────────────────────────────
        commission = instance.commission_amount
        reward_desc = instance.reward_description or '₹500 credit on your next project'

        referrer_subject = f"🎉 Your Referral Converted! — {site}"
        if commission and commission > 0:
            referrer_html = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f0fdf4;border-radius:12px;border:1px solid #86efac;">
              <h2 style="color:#15803d;">Congratulations, {instance.referrer_name}! 🎊</h2>
              <p style="color:#166534;">
                <strong>{instance.referred_name or 'Your friend'}</strong> signed up using your referral link
                and has placed a project with us. Your referral has been successfully converted!
              </p>

              <div style="background:#fff;border:2px solid #86efac;border-radius:12px;padding:24px;margin:24px 0;text-align:center;">
                <p style="font-size:12px;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;margin:0 0 6px;">Your Commission Amount</p>
                <p style="font-size:36px;font-weight:800;color:#15803d;margin:0 0 6px;">₹{commission}</p>
                <p style="color:#166534;font-size:14px;margin:0;">{reward_desc}</p>
                <span style="display:inline-block;margin-top:12px;background:#fef9c3;color:#854d0e;font-size:12px;
                              font-weight:600;padding:4px 14px;border-radius:20px;">⏳ Pending Admin Approval</span>
              </div>

              <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:18px;margin-bottom:24px;">
                <p style="color:#1d4ed8;font-weight:700;margin:0 0 10px;">📋 What happens next?</p>
                <ol style="color:#1e40af;font-size:14px;margin:0;padding-left:20px;line-height:1.8;">
                  <li>Our team reviews your referral conversion</li>
                  <li>Your commission/reward is approved within 2–3 business days</li>
                  <li>You receive a confirmation email once reward is processed</li>
                </ol>
              </div>

              <p style="color:#475569;font-size:13px;">Questions? <a href="mailto:{support}" style="color:#15803d;">{support}</a></p>
              <p style="color:#94a3b8;font-size:12px;margin-top:24px;">— The {site} Team</p>
            </div>
            """
        else:
            referrer_html = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f0fdf4;border-radius:12px;border:1px solid #86efac;">
              <h2 style="color:#15803d;">Congratulations, {instance.referrer_name}! 🎊</h2>
              <p style="color:#166534;">
                <strong>{instance.referred_name or 'Your friend'}</strong> signed up using your referral link
                and has placed a project with us. Your referral has been successfully converted!
              </p>

              <div style="background:#fff;border:2px solid #86efac;border-radius:12px;padding:20px;margin:24px 0;">
                <p style="color:#15803d;font-weight:700;margin:0 0 6px;">🎁 Your Reward</p>
                <p style="color:#166534;font-size:15px;font-weight:600;margin:0;">{reward_desc}</p>
                <p style="color:#16a34a;font-size:12px;margin:8px 0 0;">
                  Our team will review and process your reward within 2–3 business days.
                </p>
              </div>

              <p style="color:#475569;font-size:13px;">Questions? <a href="mailto:{support}" style="color:#15803d;">{support}</a></p>
              <p style="color:#94a3b8;font-size:12px;margin-top:24px;">— The {site} Team</p>
            </div>
            """

        plain_referrer = (
            f"Congratulations {instance.referrer_name}!\n\n"
            f"{instance.referred_name or 'Your friend'} signed up using your referral link.\n"
            f"Your referral has been converted!\n\n"
            f"Reward: {reward_desc}\n"
            + (f"Commission: ₹{commission} (pending admin approval)\n" if commission and commission > 0 else "")
            + f"\nOur team will process your reward within 2–3 business days.\n\n— {site}"
        )
        _send_html_email(referrer_subject, instance.referrer_email, referrer_html, plain_referrer)

        # (b) Notify admin ─────────────────────────────────────
        try:
            from .models import GlobalSettings
            gs = GlobalSettings.objects.first()
            admin_emails_raw = gs.admin_notification_emails if gs else ''
            admin_emails = [e.strip() for e in admin_emails_raw.split(',') if e.strip()]
            if not admin_emails:
                admin_emails = [settings.DEFAULT_FROM_EMAIL]

            admin_subject = f"🔔 Referral Converted — Pending Reward Approval — {site}"
            admin_html = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#fffbeb;border-radius:12px;border:1px solid #fcd34d;">
              <h2 style="color:#92400e;">Referral Converted — Action Required ⚡</h2>
              <p style="color:#78350f;">A referred person has signed up. Please review and approve the reward in admin.</p>
              <table style="width:100%;border-collapse:collapse;margin:16px 0;background:#fff;border-radius:8px;overflow:hidden;">
                <tr><td style="padding:10px;color:#64748b;font-size:13px;border-bottom:1px solid #f1f5f9;">Referrer</td><td style="padding:10px;font-weight:600;color:#0f172a;border-bottom:1px solid #f1f5f9;">{instance.referrer_name} ({instance.referrer_email})</td></tr>
                <tr><td style="padding:10px;color:#64748b;font-size:13px;border-bottom:1px solid #f1f5f9;">Referred Person</td><td style="padding:10px;color:#0f172a;border-bottom:1px solid #f1f5f9;">{instance.referred_name or '—'} ({instance.referred_email or '—'})</td></tr>
                <tr><td style="padding:10px;color:#64748b;font-size:13px;">Referral Code</td><td style="padding:10px;font-family:monospace;color:#6366f1;">{instance.referral_code}</td></tr>
              </table>
              <a href="{site_url}/admin/website/referralproxy/{instance.pk}/change/"
                 style="display:inline-block;background:#6366f1;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:8px;">
                Review &amp; Approve Reward →
              </a>
              <p style="color:#92400e;font-size:13px;margin-top:16px;">Use the <strong>"Mark selected as Rewarded"</strong> admin action to auto-generate a coupon and email the referrer.</p>
            </div>
            """
            for admin_email in admin_emails:
                _send_html_email(admin_subject, admin_email, admin_html)
        except Exception as e:
            logger.error(f'[Signal] Admin notification for referral conversion failed: {e}')

    # ── Case 3: Status changed to 'rewarded' ────────────────────
    # Admin ran "Mark selected as Rewarded" action → commission paid confirmation email to referrer
    elif prev_status and prev_status != 'rewarded' and instance.status == 'rewarded':

        commission = instance.commission_amount
        reward_desc = instance.reward_description or '₹500 credit on your next project'
        coupon_code = f"REF-{instance.referral_code.upper()}"

        referrer_subject = f"✅ Your Referral Reward has been Processed! — {site}"
        referrer_html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f0fdf4;border-radius:12px;border:1px solid #86efac;">
          <h2 style="color:#15803d;">Great News, {instance.referrer_name}! ✅</h2>
          <p style="color:#166534;">
            Your referral reward has been approved and processed by our team!
          </p>

          <div style="background:#fff;border:2px solid #4ade80;border-radius:12px;padding:24px;margin:24px 0;text-align:center;">
            <p style="font-size:12px;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;margin:0 0 6px;">Your Reward Coupon Code</p>
            <p style="font-family:monospace;font-size:28px;font-weight:800;color:#15803d;letter-spacing:3px;margin:0 0 8px;">{coupon_code}</p>
            {"<p style='font-size:20px;font-weight:700;color:#166534;margin:0 0 6px;'>₹" + str(commission) + " Commission Credited</p>" if commission and commission > 0 else ""}
            <p style="color:#166534;font-size:14px;margin:0;">{reward_desc}</p>
            <span style="display:inline-block;margin-top:10px;background:#dcfce7;color:#166534;font-size:12px;
                          font-weight:600;padding:4px 14px;border-radius:20px;">✅ Approved & Processed</span>
          </div>

          <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:16px;margin-bottom:24px;">
            <p style="color:#1d4ed8;font-weight:700;margin:0 0 8px;">💡 How to use your coupon?</p>
            <p style="color:#1e40af;font-size:13px;margin:0;">
              Apply code <strong>{coupon_code}</strong> at checkout on your next project with us.
              The discount will be applied automatically.
            </p>
          </div>

          <p style="color:#475569;font-size:13px;">Questions? <a href="mailto:{support}" style="color:#15803d;">{support}</a></p>
          <p style="color:#94a3b8;font-size:12px;margin-top:24px;">— The {site} Team</p>
        </div>
        """
        plain_referrer = (
            f"Great News, {instance.referrer_name}!\n\n"
            f"Your referral reward has been approved and processed!\n\n"
            f"Coupon Code: {coupon_code}\n"
            + (f"Commission: ₹{commission}\n" if commission and commission > 0 else "")
            + f"Reward: {reward_desc}\n\n"
            f"Apply this code at checkout on your next project.\n\n— {site}"
        )
        _send_html_email(referrer_subject, instance.referrer_email, referrer_html, plain_referrer)


# ══════════════════════════════════════════════════════════════════
# AFFILIATE SIGNALS
# ══════════════════════════════════════════════════════════════════

# Status pehle kya tha — track karne ke liye pre_save use karein
_affiliate_prev_status = {}


@receiver(pre_save, sender='website.Affiliate')
def affiliate_pre_save(sender, instance, **kwargs):
    """Save previous status before save so post_save can detect changes."""
    if instance.pk:
        try:
            from .models import Affiliate
            old = Affiliate.objects.get(pk=instance.pk)
            _affiliate_prev_status[instance.pk] = old.status
        except Exception:
            pass


@receiver(post_save, sender='website.Affiliate')
def on_affiliate_save(sender, instance, created, **kwargs):
    """
    Trigger:  Affiliate object save hone par
    Actions:
      • Naya affiliate apply kiya → admin ko notification email
      • Status 'pending' → 'active' hua → affiliate ko approval email
      • Status 'suspended' hua → affiliate ko suspension email
    """
    site    = _site_name()
    support = _support_email()
    site_url = getattr(settings, 'SITE_URL', '')
    prev_status = _affiliate_prev_status.pop(instance.pk, None)

    # ── Case 1: New application ──────────────────────────────────
    if created:
        # Notify admin
        try:
            from .models import GlobalSettings
            gs = GlobalSettings.objects.first()
            admin_emails_raw = gs.admin_notification_emails if gs else ''
            admin_emails = [e.strip() for e in admin_emails_raw.split(',') if e.strip()]
            if not admin_emails:
                admin_emails = [settings.DEFAULT_FROM_EMAIL]

            admin_subject = f"🤝 New Affiliate Application — {instance.name}"
            admin_html = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f9fafb;border-radius:12px;">
              <h2 style="color:#0f172a;">New Affiliate Application 📋</h2>
              <table style="width:100%;border-collapse:collapse;margin:16px 0;">
                <tr><td style="padding:8px;color:#64748b;font-size:13px;">Name</td><td style="padding:8px;font-weight:600;color:#0f172a;">{instance.name}</td></tr>
                <tr style="background:#f1f5f9;"><td style="padding:8px;color:#64748b;font-size:13px;">Email</td><td style="padding:8px;color:#0f172a;">{instance.email}</td></tr>
                <tr><td style="padding:8px;color:#64748b;font-size:13px;">Phone</td><td style="padding:8px;color:#0f172a;">{instance.phone or '—'}</td></tr>
                <tr style="background:#f1f5f9;"><td style="padding:8px;color:#64748b;font-size:13px;">Company</td><td style="padding:8px;color:#0f172a;">{instance.company or '—'}</td></tr>
                <tr><td style="padding:8px;color:#64748b;font-size:13px;">Website</td><td style="padding:8px;color:#0f172a;">{instance.website or '—'}</td></tr>
                <tr style="background:#f1f5f9;"><td style="padding:8px;color:#64748b;font-size:13px;">How they'll promote</td><td style="padding:8px;color:#0f172a;">{instance.how_promote or '—'}</td></tr>
              </table>
              <a href="{site_url}/admin/growth/affiliateproxy/{instance.pk}/change/"
                 style="display:inline-block;background:#6366f1;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:8px;">
                Review in Admin →
              </a>
            </div>
            """
            for admin_email in admin_emails:
                _send_html_email(admin_subject, admin_email, admin_html)
        except Exception as e:
            logger.error(f'[Signal] Admin notification for affiliate {instance.email} failed: {e}')

        # Notify applicant — application received
        subject = f"✅ Application Received — {site} Affiliate Program"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f9fafb;border-radius:12px;">
          <h2 style="color:#0f172a;">Hi {instance.name}! 👋</h2>
          <p style="color:#475569;">We've received your affiliate application. Our team will review it and get back to you within <strong>24–48 hours</strong>.</p>
          <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px;margin:24px 0;">
            <p style="color:#1e40af;font-weight:600;margin:0 0 4px;">What happens next?</p>
            <ol style="color:#1e40af;font-size:14px;margin:0;padding-left:20px;">
              <li style="margin-bottom:6px;">Our team reviews your application</li>
              <li style="margin-bottom:6px;">You receive approval + unique affiliate link</li>
              <li>You start promoting and earning commission!</li>
            </ol>
          </div>
          <p style="color:#475569;font-size:14px;">Questions? Email us at <a href="mailto:{support}">{support}</a></p>
          <p style="color:#94a3b8;font-size:12px;margin-top:32px;">— The {site} Team</p>
        </div>
        """
        plain = (
            f"Hi {instance.name},\n\nWe've received your affiliate application.\n"
            f"Our team will review and respond within 24-48 hours.\n\n— {site}"
        )
        _send_html_email(subject, instance.email, html, plain)
        return

    # ── Case 2: Status changed to 'active' ──────────────────────
    if prev_status and prev_status != 'active' and instance.status == 'active':
        aff_link = f"{site_url}/aff/{instance.affiliate_code}/"
        subject  = f"🎉 Affiliate Application Approved — {site}"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f9fafb;border-radius:12px;">
          <h2 style="color:#0f172a;">Welcome to the {site} Affiliate Program! 🚀</h2>
          <p style="color:#475569;">Great news — your affiliate application has been <strong style="color:#15803d;">approved</strong>!</p>

          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin:24px 0;">
            <p style="font-size:12px;color:#94a3b8;margin:0 0 8px;text-transform:uppercase;letter-spacing:.05em;">Your affiliate link</p>
            <p style="font-family:monospace;color:#6366f1;word-break:break-all;margin:0;">
              <a href="{aff_link}" style="color:#6366f1;">{aff_link}</a>
            </p>
            <p style="font-size:12px;color:#94a3b8;margin:8px 0 0;">Code: <strong>{instance.affiliate_code}</strong></p>
          </div>

          <div style="display:flex;gap:16px;margin:24px 0;">
            <div style="flex:1;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;">
              <p style="color:#15803d;font-weight:700;font-size:20px;margin:0 0 4px;">{instance.commission_percent}%</p>
              <p style="color:#166534;font-size:13px;margin:0;">Commission on every converted project</p>
            </div>
          </div>

          <p style="color:#475569;font-size:14px;">Share your link on social media, your blog, or your network. Every time someone places a project using your link, you earn commission!</p>
          <p style="color:#475569;font-size:14px;">Contact us at <a href="mailto:{support}">{support}</a> for any help.</p>
          <p style="color:#94a3b8;font-size:12px;margin-top:32px;">— The {site} Team</p>
        </div>
        """
        plain = (
            f"Hi {instance.name},\n\nYour affiliate application is APPROVED!\n\n"
            f"Your link: {aff_link}\n"
            f"Your code: {instance.affiliate_code}\n"
            f"Commission: {instance.commission_percent}%\n\n— {site}"
        )
        _send_html_email(subject, instance.email, html, plain)

    # ── Case 3: Status changed to 'suspended' ───────────────────
    elif prev_status and prev_status != 'suspended' and instance.status == 'suspended':
        subject = f"⚠️ Affiliate Account Suspended — {site}"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f9fafb;border-radius:12px;">
          <h2 style="color:#0f172a;">Hi {instance.name},</h2>
          <p style="color:#475569;">Your affiliate account has been temporarily suspended. Please contact us for details.</p>
          <p style="color:#475569;font-size:14px;">Email: <a href="mailto:{support}">{support}</a></p>
          <p style="color:#94a3b8;font-size:12px;margin-top:32px;">— The {site} Team</p>
        </div>
        """
        _send_html_email(subject, instance.email, html)


# ══════════════════════════════════════════════════════════════════
# AFFILIATE CONVERSION SIGNALS
# ══════════════════════════════════════════════════════════════════

_conversion_prev_status = {}


@receiver(pre_save, sender='website.AffiliateConversion')
def conversion_pre_save(sender, instance, **kwargs):
    """Save previous status before save."""
    if instance.pk:
        try:
            from .models import AffiliateConversion
            old = AffiliateConversion.objects.get(pk=instance.pk)
            _conversion_prev_status[instance.pk] = old.status
        except Exception:
            pass


@receiver(post_save, sender='website.AffiliateConversion')
def on_conversion_save(sender, instance, created, **kwargs):
    """
    Trigger:  AffiliateConversion save hone par
    Actions:
      • Naya lead → affiliate ke total_leads +1
      • Status 'lead' → 'converted':
          - Affiliate.total_converted +1
          - Affiliate.total_earned += commission
          - Affiliate ko commission earned email
      • Status 'converted' → 'paid':
          - Affiliate.total_paid_out += commission
          - Affiliate ko payment confirmation email
    """
    from .models import Affiliate

    site    = _site_name()
    support = _support_email()
    aff     = instance.affiliate
    prev    = _conversion_prev_status.pop(instance.pk, None)

    # ── Case 1: New lead created ─────────────────────────────────
    if created:
        Affiliate.objects.filter(pk=aff.pk).update(
            total_leads=aff.total_leads + 1
        )
        return

    # ── Case 2: lead → converted ─────────────────────────────────
    if prev == 'lead' and instance.status == 'converted':
        Affiliate.objects.filter(pk=aff.pk).update(
            total_converted=aff.total_converted + 1,
            total_earned=aff.total_earned + instance.commission,
        )

        site_url  = getattr(settings, 'SITE_URL', '')
        subject   = f"💰 Commission Earned — ₹{instance.commission} — {site}"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f9fafb;border-radius:12px;">
          <h2 style="color:#0f172a;">Commission Earned! 💰</h2>
          <p style="color:#475569;">A referral you sent has converted to a project. Here are the details:</p>

          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin:24px 0;">
            <table style="width:100%;border-collapse:collapse;">
              <tr><td style="padding:8px;color:#64748b;font-size:13px;">Client</td><td style="padding:8px;font-weight:600;color:#0f172a;">{instance.name}</td></tr>
              <tr style="background:#f8fafc;"><td style="padding:8px;color:#64748b;font-size:13px;">Project value</td><td style="padding:8px;color:#0f172a;">₹{instance.order_value}</td></tr>
              <tr><td style="padding:8px;color:#64748b;font-size:13px;">Your commission ({aff.commission_percent}%)</td>
                  <td style="padding:8px;font-weight:700;color:#15803d;font-size:18px;">₹{instance.commission}</td></tr>
            </table>
          </div>

          <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin:24px 0;">
            <p style="color:#15803d;font-weight:600;margin:0 0 4px;">Total earned so far</p>
            <p style="color:#166534;font-size:20px;font-weight:700;margin:0;">₹{float(aff.total_earned) + float(instance.commission)}</p>
          </div>

          <p style="color:#475569;font-size:14px;">Payouts are processed monthly. Questions? <a href="mailto:{support}">{support}</a></p>
          <p style="color:#94a3b8;font-size:12px;margin-top:32px;">— The {site} Team</p>
        </div>
        """
        plain = (
            f"Commission Earned!\n\n"
            f"Client: {instance.name}\n"
            f"Project value: ₹{instance.order_value}\n"
            f"Commission ({aff.commission_percent}%): ₹{instance.commission}\n\n"
            f"— {site}"
        )
        _send_html_email(subject, aff.email, html, plain)

    # ── Case 3: converted → paid ─────────────────────────────────
    elif prev == 'converted' and instance.status == 'paid':
        Affiliate.objects.filter(pk=aff.pk).update(
            total_paid_out=aff.total_paid_out + instance.commission,
        )

        subject = f"✅ Commission Payment Sent — ₹{instance.commission} — {site}"
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f9fafb;border-radius:12px;">
          <h2 style="color:#0f172a;">Payment Sent! ✅</h2>
          <p style="color:#475569;">Your commission for the following referral has been paid:</p>

          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin:24px 0;">
            <table style="width:100%;border-collapse:collapse;">
              <tr><td style="padding:8px;color:#64748b;font-size:13px;">Client</td><td style="padding:8px;font-weight:600;">{instance.name}</td></tr>
              <tr style="background:#f8fafc;"><td style="padding:8px;color:#64748b;font-size:13px;">Amount paid</td>
                  <td style="padding:8px;font-weight:700;color:#15803d;font-size:18px;">₹{instance.commission}</td></tr>
            </table>
          </div>

          <p style="color:#475569;font-size:14px;">Keep referring clients and earning more! Your affiliate link: <code>{getattr(settings, "SITE_URL", "")}/aff/{aff.affiliate_code}/</code></p>
          <p style="color:#94a3b8;font-size:12px;margin-top:32px;">— The {site} Team</p>
        </div>
        """
        plain = (
            f"Payment Sent!\n\n"
            f"Client: {instance.name}\n"
            f"Amount: ₹{instance.commission}\n\n— {site}"
        )
        _send_html_email(subject, aff.email, html, plain)