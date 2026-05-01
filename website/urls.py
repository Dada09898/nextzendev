from django.urls import path
from . import views

urlpatterns = [
    # ── Main pages ──────────────────────────────────────────────────────
    path('', views.home, name='home'),
    path('services', views.services, name='services'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('contact/thank-you/', views.contact_thankyou, name='contact_thankyou'), 
    # ── Legal pages ─────────────────────────────────────────────────────
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('refund/', views.refund, name='refund'),

    # ── Chatbot ──────────────────────────────────────────────────────────
    path('chatbot/', views.chatbot_api, name='chatbot_api'),
    path('chatbot/fetch/', views.fetch_messages, name='fetch_messages'),
    path('chatbot/admin-reply/', views.admin_reply, name='admin_reply'),
    path('chatbot/end/', views.end_conversation, name='end_conversation'),

    # ── AI Features ──────────────────────────────────────────────────────
    path('ai/recommend/', views.ai_recommend, name='ai_recommend'),

    # ── Coupon System ────────────────────────────────────────────────────
    path('coupons/', views.coupons_page, name='coupons'),
    path('coupons/validate/', views.validate_coupon, name='validate_coupon'),

    # ── Referral System ──────────────────────────────────────────────────
    path('referral/', views.referral_page, name='referral'),

    # ── Affiliate System ─────────────────────────────────────────────────
    path('affiliate/', views.affiliate_page, name='affiliate'),
    path('go/<str:aff_code>/', views.affiliate_track_click, name='affiliate_track'),

    # ── Lead CRM ──────────────────────────────────────────────────────────
    # (leads are created automatically — no public URL needed)

    # ── Payment System ────────────────────────────────────────────────────
    path('payment/',               views.payment_page,          name='payment'),
    path('payment/create-order/',  views.create_payment_order,  name='create_payment_order'),
    path('payment/verify/',        views.verify_payment,        name='verify_payment'),
    path('payment/success/',       views.payment_success,       name='payment_success'),

    # ── Payment OTP Verification ───────────────────────────────────────────
    path('payment/send-otp/',      views.send_payment_otp,      name='send_payment_otp'),
    path('payment/verify-otp/',    views.verify_payment_otp,    name='verify_payment_otp'),
    path('payment/resend-otp/',    views.resend_payment_otp,    name='resend_payment_otp'),

    # ── Newsletter ────────────────────────────────────────────────────────
    path('newsletter/subscribe/',  views.subscribe_newsletter,  name='subscribe_newsletter'),

    # ── Enhanced CRM Analytics ────────────────────────────────────
    path('crm/analytics/', views.analytics_dashboard, name='analytics_dashboard'),

    
    # ── Appointment System ────────────────────────────────────────
    path('appointment/',         views.appointment_page,    name='appointment'),
    path('appointment/book/',    views.book_appointment,    name='book_appointment'),
    path('appointment/confirm/', views.appointment_confirm, name='appointment_confirm'),
    
    # ── Blog / SEO ────────────────────────────────────────────────
    path('blog/',                         views.blog_list,   name='blog_list'),
    path('blog/<slug:slug>/',             views.blog_detail, name='blog_detail'),
    path('blog/category/<slug:slug>/',    views.blog_by_category, name='blog_category'),
    path('blog/tag/<slug:slug>/',         views.blog_by_tag,      name='blog_tag'),
    
    # ── Invoice Download ──────────────────────────────────────────
     path('invoice/<str:invoice_number>/download/', views.download_invoice, name='download_invoice')

     
]