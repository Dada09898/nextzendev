"""
Django settings for config project.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file (local dev only — Render pe env vars directly inject hote hain)
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False") == "True"

# ══════════════════════════════════════════════════════════════════
# ALLOWED HOSTS — single source of truth
# ══════════════════════════════════════════════════════════════════
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'nextzendev.in',
    'www.nextzendev.in',
    'nextzendev.onrender.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://nextzendev.in',
    'https://www.nextzendev.in',
    'https://nextzendev.onrender.com',
]


# ══════════════════════════════════════════════════════════════════
# JAZZMIN SETTINGS — Admin panel sections & icons
# ══════════════════════════════════════════════════════════════════

JAZZMIN_SETTINGS = {
    # ── Brand ──────────────────────────────────────────────────────
    "site_title":        "NextZen Admin",
    "site_header":       "NextZen IT Solutions",
    "site_brand":        "",
    "site_logo":         "website/images/logo.png",
    "site_logo_classes": "img-fluid",
    "site_icon":         "website/images/logo.png",
    "custom_css":        "website/css/admin_custom.css",
    "welcome_sign":      "Welcome to NextZen IT Solutions Admin",
    "copyright":         "NextZen IT Solutions",

    # ── Top nav search ─────────────────────────────────────────────
    "search_model": ["website.Lead", "website.Invoice", "website.Client"],

    # ── Top nav quick links ────────────────────────────────────────
    "topmenu_links": [
        {"name": "🌐 View Site",   "url": "/",            "new_window": True},
        {"name": "💬 Chat",        "url": "/admin/website/chatsession/"},
        {"name": "📅 Appointments","url": "/admin/website/appointment/"},
        {"name": "💳 Invoices",    "url": "/admin/website/invoice/"},
    ],

    "usermenu_links": [
        {"name": "🌐 View Site",       "url": "/",                      "new_window": True},
        {"name": "🔑 Change Password", "url": "/admin/password_change/"},
        {"name": "🚪 Logout",          "url": "/admin/logout/"},
    ],

    # ── Sidebar ────────────────────────────────────────────────────
    "show_sidebar": True,
    "navigation_expanded": True,

    # ── Sidebar menu order ─────────────────────────────────────────
    # Sections upar se neeche is order mein dikhenge
    "order_with_respect_to": [
        "website",          # ⚙️ Settings & Website Content
        "contacts",         # 📞 Contacts
        "crm",              # 👥 CRM
        "payments",         # 💳 Payments
        "chat_app",         # 💬 Chat
        "email_app",        # 📧 Email
        "bookings",         # 📅 Appointments
        "blog_app",         # ✍️ Blog
        "growth",           # 🎁 Growth
        "auth",             # 🔐 Auth
    ],

    # ── Custom links ───────────────────────────────────────────────
    "custom_links": {
        "crm": [{
            "name":        "📊 CRM Analytics",
            "url":         "/crm/analytics/",
            "icon":        "fas fa-chart-line",
            "permissions": ["website.view_lead"],
        }],
    },

    # ── Icons (Font Awesome 5) ─────────────────────────────────────
    "icons": {
        # Auth
        "auth":                          "fas fa-users-cog",
        "auth.user":                     "fas fa-user",
        "auth.Group":                    "fas fa-users",

        # ⚙️ Website / Settings
        "website.GlobalSettings":        "fas fa-sliders-h",
        "website.SiteSettings":          "fas fa-cog",
        "website.SocialMedia":           "fas fa-share-alt",
        "website.SiteContent":           "fas fa-file-alt",
        "website.HeroSection":           "fas fa-image",
        "website.Hero":                  "fas fa-image",
        "website.Service":               "fas fa-concierge-bell",
        "website.Portfolio":             "fas fa-briefcase",
        "website.Testimonial":           "fas fa-star",
        "website.TrustedClient":         "fas fa-handshake",
        "website.WhyChooseUs":           "fas fa-check-circle",
        "website.ProcessStep":           "fas fa-list-ol",
        "website.PricingPlan":           "fas fa-tags",
        "website.FAQ":                   "fas fa-question-circle",

        # 📞 Contacts
        "contacts.contactproxy":         "fas fa-envelope-open-text",
        "contacts.contactleadproxy":     "fas fa-user-plus",

        # 👥 CRM
        "crm.leadproxy":                 "fas fa-funnel-dollar",
        "crm.clientproxy":               "fas fa-user-tie",
        "crm.projectproxy":              "fas fa-project-diagram",
        "crm.communicationlogproxy":     "fas fa-comments",
        "crm.taskproxy":                 "fas fa-tasks",

        # 💳 Payments
        "payments.paymentorderproxy":    "fas fa-credit-card",
        "payments.invoiceproxy":         "fas fa-file-invoice-dollar",

        # 💬 Chat
        "chat_app.chatsessionproxy":     "fas fa-comment-dots",
        "chat_app.chatmessageproxy":     "fas fa-comment",

        # 📧 Email
        "email_app.emailtemplateproxy":  "fas fa-envelope",
        "email_app.emaillogproxy":       "fas fa-paper-plane",
        "email_app.newslettersubscriberproxy": "fas fa-newspaper",

        # 📅 Bookings
        "bookings.appointmentproxy":     "fas fa-calendar-check",

        # ✍️ Blog
        "blog_app.blogpostproxy":        "fas fa-pen-nib",
        "blog_app.blogcategoryproxy":    "fas fa-folder",
        "blog_app.blogtagproxy":         "fas fa-hashtag",

        # 🎁 Growth
        "growth.couponproxy":            "fas fa-ticket-alt",
        "growth.couponusageproxy":       "fas fa-receipt",
        "growth.referralproxy":          "fas fa-user-friends",
        "growth.affiliateproxy":         "fas fa-link",
        "growth.affiliateconversionproxy": "fas fa-trophy",
    },

    "default_icon_parents":  "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # ── UI ─────────────────────────────────────────────────────────
    "related_modal_active": True,
    "show_ui_builder":      False,
    "changeform_format":    "horizontal_tabs",
    "language_chooser":     False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text":       False,
    "footer_small_text":       False,
    "body_small_text":         False,
    "brand_small_text":        False,
    "brand_colour":            "navbar-dark",
    "accent":                  "accent-primary",
    "navbar":                  "navbar-dark",
    "no_navbar_border":        True,
    "navbar_fixed":            True,
    "layout_boxed":            False,
    "footer_fixed":            False,
    "sidebar_fixed":           True,
    "sidebar":                 "sidebar-dark-primary",
    "sidebar_nav_small_text":  False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_flat_style":  False,
    "theme":                   "default",
    "dark_mode_theme":         None,
    "button_classes": {
        "primary":   "btn-primary",
        "secondary": "btn-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
}


# ══════════════════════════════════════════════════════════════════
# INSTALLED APPS
# NOTE: 'jazzmin' MUST be first — django.contrib.admin se pehle
# ══════════════════════════════════════════════════════════════════

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'cloudinary_storage',
    'website',
    'contacts',
    'crm',
    'payments',
    'chat_app',
    'email_app',
    'bookings',
    'blog_app',
    'growth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # ← MUST be first
    'whitenoise.middleware.WhiteNoiseMiddleware',     # ← right after Security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'website.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':[],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'website.context_processors.social_links',
                'website.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

_db_url = os.getenv('DATABASE_URL')

if _db_url:
    DATABASES = {
        'default': dj_database_url.parse(
            _db_url,
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
SITE_URL = os.getenv('SITE_URL', 'https://nextzendev.in')

# ── Security Headers (production only) ───────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT             = True
    SECURE_HSTS_SECONDS             = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
    SECURE_HSTS_PRELOAD             = True
    SECURE_BROWSER_XSS_FILTER       = True
    SECURE_CONTENT_TYPE_NOSNIFF     = True
    X_FRAME_OPTIONS                 = 'DENY'
    SESSION_COOKIE_SECURE           = True
    CSRF_COOKIE_SECURE              = True
    SESSION_COOKIE_HTTPONLY         = True
    CSRF_COOKIE_HTTPONLY            = True

USE_I18N = True
USE_TZ = True

# ── Static & Media ────────────────────────────────────────────────
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY':    os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [BASE_DIR / "website" / "static"]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
SITE_NAME = 'NextZen IT Solutions'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp-relay.brevo.com')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False') == 'True'
# EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True') == 'True'
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'NextZen IT Solutions <connect@nextzendev.in>')
EMAIL_TIMEOUT = 10
EMAIL_BACKEND = 'config.brevo_backend.BrevoEmailBackend'
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
DEFAULT_FROM_EMAIL = 'NextZen IT Solutions <connect@nextzendev.in>'
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM        = os.getenv("TWILIO_FROM")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'website': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'