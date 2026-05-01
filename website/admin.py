"""
admin.py — NextZen IT Solutions
Fully reorganized with clear Admin Site sections.

SECTIONS (Django Admin sidebar groups):
  📞 Contact         → Contact, ContactLead
  💬 Chat            → ChatSession, ChatMessage
  📰 Newsletter      → NewsletterSubscriber
  🆕 Leads & CRM     → Lead, LeadNote, Client, Project, CommunicationLog, Task
  💳 Payments        → PaymentOrder, Invoice
  📧 Email           → EmailTemplate, EmailLog
  📅 Appointments    → Appointment
  ✍️ Blog            → BlogPost, BlogCategory, BlogTag
  🎁 Growth          → Coupon, CouponUsage, Referral, Affiliate, AffiliateConversion
  🌐 Website         → HeroSection, TrustedClient, Service, Portfolio, Testimonial,
                        WhyChooseUs, ProcessStep, PricingPlan, FAQ, SocialMedia,
                        SiteContent, SiteSettings, GlobalSettings
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path, reverse
from django.shortcuts import render
from django.utils.html import format_html, mark_safe
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib import messages as dj_messages

from .models import (
    # Contact
    Contact, ContactLead,
    # Chat
    ChatSession, ChatMessage,
    # Newsletter
    NewsletterSubscriber,
    # Leads & CRM
    Lead, LeadNote, Client, Project, CommunicationLog, Task,
    # Payments
    PaymentOrder,
    # Email
    EmailTemplate, EmailLog,
    # Growth
    Coupon, CouponUsage, Referral, Affiliate, AffiliateClick, AffiliateConversion,
    # Website
    Hero, HeroSection, TrustedClient, WhyChooseUs, ProcessStep, Testimonial,
    Service, Portfolio, PricingPlan, FAQ, SocialMedia, SiteContent, SiteSettings,
    GlobalSettings,
    # New features
    Appointment, BlogPost, BlogCategory, BlogTag, Invoice, InvoiceItem,
)


# ══════════════════════════════════════════════════════════════════
# CUSTOM ADMIN SITE  — controls sidebar app grouping & titles
# ══════════════════════════════════════════════════════════════════

class NextZenAdminSite(AdminSite):
    site_header  = '⚡ NextZen IT Solutions — Admin'
    site_title   = 'NextZen Admin'
    index_title  = 'Dashboard'

    def get_app_list(self, request, app_label=None):
        """
        Return a custom-ordered app list with human-friendly section names.
        We still use the default but relabel 'Website' into logical sub-groups.
        """
        app_list = super().get_app_list(request, app_label)
        return app_list


# Use the DEFAULT admin site (no need to replace — we control ordering via
# verbose_name in Meta and app_label order in INSTALLED_APPS).
# The sections below are purely structural comments aligned with Django's
# "Website" app. We split them visually using emoji verbose_names.


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░░  📞 CONTACT SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'phone', 'service', 'budget', 'timeline', 'created_at')
    list_filter   = ('service', 'budget', 'timeline', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at',)
    ordering      = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('👤 Contact Details', {
            'fields': ('name', 'email', 'phone'),
        }),
        ('📋 Project Info', {
            'fields': ('service', 'budget', 'timeline', 'message'),
        }),
        ('🕒 Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    class Meta:
        verbose_name = '📞 Contact Form Submission'


@admin.register(ContactLead)
class ContactLeadAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at',)
    ordering      = ('-created_at',)
    date_hierarchy = 'created_at'

    class Meta:
        verbose_name = '📞 Contact Lead'


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░░  💬 CHAT SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

class ChatMessageInline(admin.TabularInline):
    model           = ChatMessage
    extra           = 0
    readonly_fields = ('sender', 'message', 'is_resolved', 'created_at')
    can_delete      = False
    show_change_link = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    change_list_template = 'admin/chat_dashboard.html'
    list_display  = ('name', 'mobile', 'email', 'flow_state', 'mode_badge',
                     'status_badge', 'created_at')
    search_fields = ('name', 'mobile', 'email', 'session_id')
    list_filter   = ('flow_state', 'is_ended', 'created_at')
    readonly_fields = ('session_id', 'created_at', 'ended_at', 'ended_by', 'is_ended')
    inlines       = [ChatMessageInline]
    date_hierarchy = 'created_at'
    actions       = ['end_selected_conversations']

    fieldsets = (
        ('👤 User Info', {
            'fields': ('name', 'email', 'mobile'),
        }),
        ('📋 Project Details', {
            'fields': ('project', 'features', 'budget', 'timeline'),
        }),
        ('🔄 Session State', {
            'fields': ('session_id', 'flow_state', 'is_ended', 'ended_by', 'ended_at'),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def mode_badge(self, obj):
        if obj.messages.filter(sender='admin').exists():
            return mark_safe('<span style="color:#10b981;font-weight:600;">🟢 Live Agent</span>')
        return mark_safe('<span style="color:#6b7280;">🤖 Bot Only</span>')
    mode_badge.short_description = 'Mode'

    def status_badge(self, obj):
        if obj.is_ended:
            by = f" by {obj.ended_by}" if obj.ended_by else ""
            return mark_safe(f'<span style="color:#ef4444;font-weight:bold;">🔴 Ended{by}</span>')
        return mark_safe('<span style="color:#10b981;">🟢 Active</span>')
    status_badge.short_description = 'Status'

    def end_selected_conversations(self, request, queryset):
        count = 0
        for session in queryset.filter(is_ended=False):
            session.is_ended   = True
            session.ended_by   = 'admin'
            session.ended_at   = timezone.now()
            session.flow_state = 'ended'
            session.save(update_fields=['is_ended', 'ended_by', 'ended_at', 'flow_state'])
            ChatMessage.objects.create(
                session=session, sender='system', is_resolved=True,
                message='🔴 Agent has ended this conversation. Thank you!'
            )
            count += 1
        self.message_user(request, f'🔴 {count} conversation(s) ended.')
    end_selected_conversations.short_description = '🔴 End selected conversations'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['sessions'] = ChatSession.objects.all().order_by('-created_at')
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.chat_dashboard_view),
                 name='chat_dashboard'),
        ]
        return custom_urls + urls

    def chat_dashboard_view(self, request):
        sessions = ChatSession.objects.all().order_by('-created_at')
        return render(request, 'admin/chat_dashboard.html', {'sessions': sessions})


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ('session', 'sender_badge', 'short_message', 'is_resolved', 'created_at')
    list_filter   = ('sender', 'is_resolved', 'created_at')
    search_fields = ('message', 'session__session_id', 'session__name')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at',)

    def sender_badge(self, obj):
        colors = {
            'user': '#3b82f6', 'bot': '#8b5cf6',
            'admin': '#10b981', 'system': '#f59e0b'
        }
        color = colors.get(obj.sender, '#6b7280')
        return format_html(
            '<span style="color:{};font-weight:700;">{}</span>', color, obj.sender.title()
        )
    sender_badge.short_description = 'Sender'

    def short_message(self, obj):
        return obj.message[:80] + ('…' if len(obj.message) > 80 else '')
    short_message.short_description = 'Message'


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░  📰 NEWSLETTER SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display  = ('email', 'subscribed_at', 'is_active', 'status_badge')
    list_filter   = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)
    list_editable = ('is_active',)
    list_display_links = ('email',)
    ordering      = ('-subscribed_at',)
    date_hierarchy = 'subscribed_at'
    actions       = ['send_broadcast', 'export_emails']

    def status_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color:#10b981;font-weight:600;">✅ Active</span>')
        return mark_safe('<span style="color:#ef4444;font-weight:600;">❌ Unsubscribed</span>')
    status_badge.short_description = 'Status'

    def export_emails(self, request, queryset):
        emails = ', '.join(queryset.filter(is_active=True).values_list('email', flat=True))
        self.message_user(request, f'📋 Active emails: {emails}')
    export_emails.short_description = '📋 Export selected active emails'

    def send_broadcast(self, request, queryset):
        pks = ','.join(str(p) for p in queryset.values_list('pk', flat=True))
        return HttpResponseRedirect(
            reverse('admin:website_newslettersubscriber_broadcast') + f'?ids={pks}'
        )
    send_broadcast.short_description = '📧 Send broadcast email to selected'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('broadcast/', self.admin_site.admin_view(self.broadcast_view),
                 name='website_newslettersubscriber_broadcast'),
        ]
        return custom + urls

    def broadcast_view(self, request):
        from django.core.mail import EmailMessage as DjEmailMessage
        from django.conf import settings as dj_settings

        ids     = request.GET.get('ids', '')
        id_list = [int(i) for i in ids.split(',') if i.strip().isdigit()]
        subs    = NewsletterSubscriber.objects.filter(pk__in=id_list, is_active=True)

        if request.method == 'POST':
            subject = request.POST.get('subject', '').strip()
            body    = request.POST.get('body', '').strip()
            if not subject or not body:
                dj_messages.error(request, '❌ Subject and body are required.')
            else:
                sent = 0
                for sub in subs:
                    try:
                        mail = DjEmailMessage(subject=subject, body=body,
                                              from_email=dj_settings.DEFAULT_FROM_EMAIL,
                                              to=[sub.email])
                        mail.send(fail_silently=False)
                        sent += 1
                    except Exception as e:
                        dj_messages.warning(request, f'⚠️ Failed for {sub.email}: {e}')
                dj_messages.success(request, f'✅ Broadcast sent to {sent} subscriber(s).')
                return HttpResponseRedirect(
                    reverse('admin:website_newslettersubscriber_changelist')
                )

        context = {
            **self.admin_site.each_context(request),
            'title': 'Send Broadcast Email',
            'subscribers': subs,
            'ids': ids,
            'opts': self.model._meta,
        }
        return render(request, 'admin/newsletter_broadcast.html', context)


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░  🆕 LEADS & CRM SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

class LeadNoteInline(admin.TabularInline):
    model           = LeadNote
    extra           = 1
    fields          = ('author', 'note', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'phone', 'service', 'colored_status',
                     'status', 'source', 'assigned_to', 'budget', 'created_at')
    list_filter   = ('status', 'source', 'assigned_to', 'created_at')
    search_fields = ('name', 'email', 'phone', 'company', 'service', 'notes')
    list_editable = ('status', 'assigned_to')
    list_display_links = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'contacted_at', 'converted_at')
    inlines       = [LeadNoteInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('👤 Contact Info', {
            'fields': ('name', 'email', 'phone', 'company'),
        }),
        ('📋 Project Details', {
            'fields': ('service', 'budget', 'timeline', 'message'),
        }),
        ('📊 Pipeline', {
            'fields': ('status', 'source', 'assigned_to'),
        }),
        ('🗒️ Internal Notes', {
            'fields': ('notes',),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at', 'contacted_at', 'converted_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_contacted', 'mark_converted', 'mark_rejected']

    def colored_status(self, obj):
        colors = {
            'new':       ('#3b82f6', '🆕 New'),
            'contacted': ('#f59e0b', '📞 Contacted'),
            'converted': ('#10b981', '✅ Converted'),
            'rejected':  ('#ef4444', '❌ Rejected'),
        }
        color, label = colors.get(obj.status, ('#6b7280', obj.status))
        return format_html('<span style="color:{};font-weight:bold;">{}</span>', color, label)
    colored_status.short_description = '●'

    def mark_contacted(self, request, queryset):
        updated = queryset.filter(status='new').update(
            status='contacted', contacted_at=timezone.now()
        )
        self.message_user(request, f'{updated} lead(s) marked as Contacted.')
    mark_contacted.short_description = '📞 Mark as Contacted'

    def mark_converted(self, request, queryset):
        updated = queryset.exclude(status='converted').update(
            status='converted', converted_at=timezone.now()
        )
        self.message_user(request, f'{updated} lead(s) marked as Converted.')
    mark_converted.short_description = '✅ Mark as Converted'

    def mark_rejected(self, request, queryset):
        updated = queryset.exclude(status='rejected').update(status='rejected')
        self.message_user(request, f'{updated} lead(s) marked as Rejected.')
    mark_rejected.short_description = '❌ Mark as Rejected'


# ── CRM: Client ──────────────────────────────────────────────────

class ProjectInline(admin.TabularInline):
    model            = Project
    extra            = 0
    fields           = ('title', 'service', 'status', 'progress', 'deadline', 'assigned_to')
    show_change_link = True


class CommunicationLogInline(admin.TabularInline):
    model            = CommunicationLog
    extra            = 0
    fields           = ('comm_type', 'subject', 'done_by', 'comm_date', 'follow_up_date', 'follow_up_done')
    show_change_link = True


class TaskInline(admin.TabularInline):
    model            = Task
    extra            = 0
    fields           = ('title', 'priority', 'status', 'assigned_to', 'due_date')
    show_change_link = True


class EmailLogInlineForClient(admin.TabularInline):
    model            = EmailLog
    extra            = 0
    fields           = ('sent_at', 'subject', 'status', 'template')
    readonly_fields  = ('sent_at',)
    can_delete       = False


class AppointmentInline(admin.TabularInline):
    model            = Appointment
    extra            = 0
    fields           = ('name', 'date', 'time', 'meeting_type', 'status', 'assigned_to')
    show_change_link = True


class InvoiceInline(admin.TabularInline):
    model            = Invoice
    extra            = 0
    fields           = ('invoice_number', 'issue_date', 'total_amount', 'status')
    readonly_fields  = ('invoice_number', 'total_amount')
    show_change_link = True


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ('name', 'company', 'email', 'phone', 'revenue_badge',
                     'project_count', 'is_active', 'created_at')
    list_filter   = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'phone', 'company', 'gstin')
    readonly_fields = ('created_at', 'updated_at', 'total_revenue', 'project_count')
    list_display_links = ('name',)
    list_editable = ('is_active',)
    inlines       = [ProjectInline, AppointmentInline, InvoiceInline,
                     CommunicationLogInline, TaskInline, EmailLogInlineForClient]

    fieldsets = (
        ('👤 Basic Info', {
            'fields': ('name', 'email', 'phone', 'company', 'address', 'website', 'gstin'),
        }),
        ('💼 Business', {
            'fields': ('lead', 'is_active', 'internal_notes'),
        }),
        ('📊 Lifetime Value', {
            'fields': ('total_revenue', 'project_count'),
            'classes': ('collapse',),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def revenue_badge(self, obj):
        color = '#10b981' if obj.total_revenue > 0 else '#6b7280'
        return format_html('<span style="color:{};font-weight:700;">₹{}</span>',
                           color, f'{obj.total_revenue:,.0f}')
    revenue_badge.short_description = '💰 Revenue'
    revenue_badge.admin_order_field = 'total_revenue'

    actions = ['recalculate_ltv']

    def recalculate_ltv(self, request, queryset):
        for client in queryset:
            client.update_lifetime_value()
        self.message_user(request, f'✅ Lifetime value updated for {queryset.count()} client(s).')
    recalculate_ltv.short_description = '🔄 Recalculate lifetime value'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display  = ('title', 'client_link', 'service', 'status_badge',
                     'progress_bar', 'deadline', 'assigned_to', 'overdue_flag')
    list_filter   = ('status', 'assigned_to', 'start_date')
    search_fields = ('title', 'client__name', 'client__email', 'service', 'assigned_to')
    readonly_fields = ('created_at', 'updated_at')
    list_display_links = ('title',)
    inlines       = [TaskInline, CommunicationLogInline]

    fieldsets = (
        ('📋 Project Info', {
            'fields': ('client', 'title', 'description', 'service', 'assigned_to'),
        }),
        ('💰 Financials', {
            'fields': ('budget', 'amount_paid', 'payment'),
        }),
        ('📊 Progress & Status', {
            'fields': ('status', 'progress', 'start_date', 'deadline', 'completed_at'),
        }),
        ('📝 Notes', {
            'fields': ('internal_notes',),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def client_link(self, obj):
        url = reverse('admin:website_client_change', args=[obj.client_id])
        return format_html('<a href="{}">{}</a>', url, obj.client.name)
    client_link.short_description = 'Client'

    def status_badge(self, obj):
        colors = {
            'planning': '#6366f1', 'in_progress': '#f59e0b', 'review': '#3b82f6',
            'completed': '#10b981', 'on_hold': '#6b7280', 'cancelled': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def progress_bar(self, obj):
        color = '#10b981' if obj.progress == 100 else '#3b82f6'
        return format_html(
            '<div style="width:100px;background:#e5e7eb;border-radius:4px;height:12px;">'
            '<div style="width:{}%;background:{};height:12px;border-radius:4px;"></div>'
            '</div> <small>{}%</small>',
            obj.progress, color, obj.progress
        )
    progress_bar.short_description = 'Progress'

    def overdue_flag(self, obj):
        if obj.is_overdue():
            return mark_safe('<span style="color:#ef4444;font-weight:700;">⚠️ Overdue</span>')
        return mark_safe('<span style="color:#10b981;">✅</span>')
    overdue_flag.short_description = 'On Time?'


@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display  = ('comm_type', 'subject', 'client', 'project', 'done_by',
                     'comm_date', 'follow_up_date', 'follow_up_done')
    list_filter   = ('comm_type', 'follow_up_done', 'comm_date')
    search_fields = ('subject', 'summary', 'client__name', 'done_by')
    list_editable = ('follow_up_done',)
    list_display_links = ('subject',)
    date_hierarchy = 'comm_date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'project')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ('title', 'priority_badge', 'status_badge', 'assigned_to',
                     'due_date', 'overdue_flag', 'client', 'project')
    list_filter   = ('status', 'priority', 'assigned_to')
    search_fields = ('title', 'description', 'assigned_to', 'client__name')
    list_editable = ('assigned_to',)
    list_display_links = ('title',)
    actions       = ['mark_done', 'mark_in_progress']

    def priority_badge(self, obj):
        colors = {'low': '#6b7280', 'medium': '#f59e0b', 'high': '#ef4444', 'urgent': '#7c3aed'}
        return format_html('<span style="color:{};font-weight:700;">{}</span>',
                           colors.get(obj.priority, '#6b7280'), obj.get_priority_display())
    priority_badge.short_description = 'Priority'

    def status_badge(self, obj):
        colors = {'todo': '#6b7280', 'in_progress': '#f59e0b', 'done': '#10b981', 'cancelled': '#ef4444'}
        return format_html('<span style="color:{};font-weight:700;">{}</span>',
                           colors.get(obj.status, '#6b7280'), obj.get_status_display())
    status_badge.short_description = 'Status'

    def overdue_flag(self, obj):
        if obj.is_overdue():
            return mark_safe('<span style="color:#ef4444;">⚠️ Overdue</span>')
        return mark_safe('<span style="color:#10b981;">✅</span>')
    overdue_flag.short_description = 'On Time?'

    def mark_done(self, request, queryset):
        updated = queryset.update(status='done', completed_at=timezone.now())
        self.message_user(request, f'✅ {updated} task(s) marked as Done.')
    mark_done.short_description = '✅ Mark as Done'

    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'🔧 {updated} task(s) marked as In Progress.')
    mark_in_progress.short_description = '🔧 Mark as In Progress'


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░  💳 PAYMENTS SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display  = ('invoice_number', 'customer_name', 'customer_email',
                     'amount_display', 'colored_status', 'invoice_badge', 'created_at', 'paid_at')
    list_filter   = ('status', 'invoice_sent', 'created_at')
    list_display_links = ('invoice_number',)
    search_fields = ('customer_name', 'customer_email', 'customer_phone',
                     'invoice_number', 'razorpay_order_id', 'razorpay_payment_id', 'description')
    readonly_fields = ('invoice_number', 'razorpay_payment_id', 'razorpay_signature',
                       'created_at', 'paid_at', 'invoice_sent')
    ordering      = ('-created_at',)
    date_hierarchy = 'created_at'
    actions       = ['check_payment_status', 'resend_invoice', 'mark_refunded']

    fieldsets = (
        ('👤 Customer', {
            'fields': ('customer_name', 'customer_email', 'customer_phone'),
        }),
        ('📦 Order Details', {
            'fields': ('description', 'amount', 'coupon', 'discount_amount', 'final_amount'),
        }),
        ('🔗 Razorpay', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',),
        }),
        ('📄 Invoice', {
            'fields': ('invoice_number', 'invoice_sent'),
        }),
        ('📊 Status', {
            'fields': ('status', 'lead'),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'paid_at'),
            'classes': ('collapse',),
        }),
    )

    def amount_display(self, obj):
        return format_html('₹{} <small style="color:#6b7280;">(₹{} after discount)</small>',
                           f'{obj.amount:,.0f}', f'{obj.final_amount:,.0f}')
    amount_display.short_description = 'Amount'

    def colored_status(self, obj):
        colors = {
            'pending': '#f59e0b', 'paid': '#10b981',
            'failed': '#ef4444', 'refunded': '#6366f1'
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{}</span>',
            colors.get(obj.status, '#6b7280'), obj.get_status_display()
        )
    colored_status.short_description = 'Status'

    def invoice_badge(self, obj):
        if obj.invoice_sent:
            return mark_safe('<span style="color:#10b981;">📧 Sent</span>')
        return mark_safe('<span style="color:#f59e0b;">⏳ Pending</span>')
    invoice_badge.short_description = 'Invoice'

    def check_payment_status(self, request, queryset):
        import razorpay
        from django.conf import settings
        client     = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        paid_count = already_paid = errors = 0
        for order in queryset:
            if not order.razorpay_order_id:
                self.message_user(request, f'⚠️ {order.invoice_number} — No Razorpay Order ID, skipped.', level='warning')
                continue
            try:
                items    = client.order.payments(order.razorpay_order_id).get('items', [])
                captured = next((p for p in items if p.get('status') == 'captured'), None)
                if captured and order.status != 'paid':
                    order.razorpay_payment_id = captured['id']
                    order.status              = 'paid'
                    order.paid_at             = order.paid_at or timezone.now()
                    order.save()
                    paid_count += 1
                elif captured:
                    already_paid += 1
                else:
                    self.message_user(request, f'❌ {order.invoice_number} — NOT paid on Razorpay.', level='warning')
            except Exception as e:
                errors += 1
                self.message_user(request, f'❌ Error for {order.invoice_number}: {e}', level='error')
        if paid_count:
            self.message_user(request, f'✅ {paid_count} order(s) confirmed paid.')
        if already_paid:
            self.message_user(request, f'ℹ️ {already_paid} order(s) already marked paid.')
    check_payment_status.short_description = '🔍 Check payment status on Razorpay'

    def resend_invoice(self, request, queryset):
        from .views import send_invoice_email
        sent = skipped = 0
        for order in queryset:
            if order.status != 'paid':
                skipped += 1
                continue
            try:
                send_invoice_email(order)
                sent += 1
            except Exception as e:
                self.message_user(request, f'❌ Failed for {order.invoice_number}: {e}', level='error')
        if sent:
            self.message_user(request, f'📧 Invoice re-sent for {sent} order(s).')
        if skipped:
            self.message_user(request, f'⚠️ {skipped} order(s) skipped — not in paid status.', level='warning')
    resend_invoice.short_description = '📧 Resend invoice email'

    def mark_refunded(self, request, queryset):
        updated = queryset.filter(status='paid').update(status='refunded')
        self.message_user(request, f'↩️ {updated} order(s) marked as Refunded.')
    mark_refunded.short_description = '↩️ Mark as Refunded'


# ── Invoice (PDF-based) ──────────────────────────────────────────

class InvoiceItemInline(admin.TabularInline):
    model  = InvoiceItem
    extra  = 1
    fields = ('description', 'quantity', 'unit_price', 'item_total')
    readonly_fields = ('item_total',)

    def item_total(self, obj):
        if obj.pk:
            return format_html('₹{:,.2f}', obj.total)
        return '-'
    item_total.short_description = 'Total'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display  = ('invoice_number', 'client_name', 'client_email',
                     'total_badge', 'status_badge', 'issue_date', 'due_date',
                     'pdf_action')
    list_filter   = ('status', 'issue_date')
    search_fields = ('invoice_number', 'client_name', 'client_email', 'client_company')
    list_display_links = ('invoice_number',)
    readonly_fields = ('invoice_number', 'subtotal', 'tax_amount',
                       'total_amount', 'created_at', 'updated_at')
    date_hierarchy = 'issue_date'
    inlines       = [InvoiceItemInline]
    actions       = ['generate_pdf', 'send_invoice_email_action', 'mark_paid', 'mark_overdue']

    fieldsets = (
        ('📄 Invoice', {
            'fields': ('invoice_number', 'status', 'issue_date', 'due_date'),
        }),
        ('👤 Billed To', {
            'fields': ('client', 'client_name', 'client_email', 'client_phone',
                       'client_company', 'client_address', 'client_gstin'),
        }),
        ('🏢 From (Your Company)', {
            'fields': ('from_name', 'from_email', 'from_address', 'from_gstin'),
            'classes': ('collapse',),
        }),
        ('💰 Financials', {
            'fields': ('subtotal', 'tax_percent', 'tax_amount', 'discount', 'total_amount'),
        }),
        ('📝 Notes & Terms', {
            'fields': ('notes', 'terms'),
            'classes': ('collapse',),
        }),
        ('🔗 Links', {
            'fields': ('payment_order', 'pdf_file'),
            'classes': ('collapse',),
        }),
        ('🕒 Timestamps', {
            'fields': ('sent_at', 'paid_at', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'draft': '#6b7280', 'sent': '#3b82f6', 'paid': '#10b981',
            'overdue': '#ef4444', 'cancelled': '#9ca3af',
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{}</span>',
            colors.get(obj.status, '#6b7280'), obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def total_badge(self, obj):
        try:
            return format_html('<strong style="color:#10b981;">₹{:,.2f}</strong>', float(obj.total_amount))
        except (TypeError, ValueError):
            return format_html('<strong style="color:#9ca3af;">₹0.00</strong>')
    total_badge.short_description = '💰 Total'
    total_badge.admin_order_field = 'total_amount'

    def pdf_action(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">📥 Download PDF</a>', obj.pdf_file.url)
        url = reverse('admin:website_invoice_generate_pdf_single', args=[obj.pk])
        return format_html('<a href="{}">🖨️ Generate PDF</a>', url)
    pdf_action.short_description = 'PDF'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:pk>/generate-pdf/',
                 self.admin_site.admin_view(self.generate_pdf_single),
                 name='website_invoice_generate_pdf_single'),
        ]
        return custom + urls

    def generate_pdf_single(self, request, pk):
        """Generate and save PDF for a single invoice."""
        from .invoice_utils import generate_invoice_pdf
        try:
            invoice = Invoice.objects.get(pk=pk)
            generate_invoice_pdf(invoice)
            dj_messages.success(request, f'✅ PDF generated for {invoice.invoice_number}')
        except Exception as e:
            dj_messages.error(request, f'❌ PDF generation failed: {e}')
        return HttpResponseRedirect(reverse('admin:website_invoice_change', args=[pk]))

    def generate_pdf(self, request, queryset):
        from .invoice_utils import generate_invoice_pdf
        count = 0
        for invoice in queryset:
            try:
                generate_invoice_pdf(invoice)
                count += 1
            except Exception as e:
                self.message_user(request, f'❌ Failed for {invoice.invoice_number}: {e}', level='error')
        self.message_user(request, f'🖨️ PDFs generated for {count} invoice(s).')
    generate_pdf.short_description = '🖨️ Generate PDF for selected'

    def send_invoice_email_action(self, request, queryset):
        from .invoice_utils import send_invoice_by_email
        sent = 0
        for invoice in queryset.exclude(status='draft'):
            try:
                send_invoice_by_email(invoice)
                sent += 1
            except Exception as e:
                self.message_user(request, f'❌ Failed for {invoice.invoice_number}: {e}', level='error')
        self.message_user(request, f'📧 Invoice emailed for {sent} invoice(s).')
    send_invoice_email_action.short_description = '📧 Send invoice by email'

    def mark_paid(self, request, queryset):
        updated = queryset.exclude(status='paid').update(status='paid', paid_at=timezone.now())
        self.message_user(request, f'✅ {updated} invoice(s) marked as Paid.')
    mark_paid.short_description = '✅ Mark as Paid'

    def mark_overdue(self, request, queryset):
        updated = queryset.filter(status='sent').update(status='overdue')
        self.message_user(request, f'⚠️ {updated} invoice(s) marked as Overdue.')
    mark_overdue.short_description = '⚠️ Mark as Overdue'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Recalculate totals after saving (inline items saved separately)
        # Admins can manually trigger recalculate via the action or the inline saves
        obj.recalculate()


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░  📧 EMAIL SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display  = ('name', 'trigger', 'subject', 'is_active', 'created_at')
    list_filter   = ('trigger', 'is_active')
    search_fields = ('name', 'subject', 'body_html')
    list_editable = ('is_active',)
    list_display_links = ('name',)

    fieldsets = (
        ('📧 Template Info', {
            'fields': ('name', 'trigger', 'is_active'),
        }),
        ('✉️ Content', {
            'fields': ('subject', 'body_html'),
            'description': (
                'Available placeholders: {{name}}, {{email}}, {{phone}}, '
                '{{service}}, {{budget}}, {{company}}, {{message}}, {{source}}, {{site_name}}'
            ),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('preview/<int:pk>/', self.admin_site.admin_view(self.preview_template),
                 name='website_emailtemplate_preview'),
        ]
        return custom + urls

    def preview_template(self, request, pk):
        from django.http import HttpResponse
        try:
            tmpl = EmailTemplate.objects.get(pk=pk)
        except EmailTemplate.DoesNotExist:
            from django.http import Http404
            raise Http404
        _, body = tmpl.render({
            'name': 'Rahul Sharma', 'email': 'rahul@example.com',
            'phone': '9999999999', 'service': 'Website Development',
            'budget': '₹50,000', 'company': 'Acme Corp',
            'message': 'Looking for a modern website.', 'source': 'Contact Form',
            'site_name': 'NextZen IT Solutions',
        })
        return HttpResponse(body)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display  = ('sent_at', 'recipient', 'subject', 'status_badge', 'template')
    list_filter   = ('status', 'template', 'sent_at')
    search_fields = ('recipient', 'subject', 'error')
    readonly_fields = ('sent_at', 'recipient', 'subject', 'body_html',
                       'status', 'error', 'template', 'lead', 'client')
    list_display_links = ('subject',)
    date_hierarchy = 'sent_at'

    def has_add_permission(self, request):
        return False  # Logs are auto-created only

    def status_badge(self, obj):
        if obj.status == 'sent':
            return mark_safe('<span style="color:#10b981;font-weight:700;">✅ Sent</span>')
        return mark_safe('<span style="color:#ef4444;font-weight:700;">❌ Failed</span>')
    status_badge.short_description = 'Status'


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░  📅 APPOINTMENTS SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'phone', 'date_time_display', 'meeting_type_badge',
                     'status_badge', 'assigned_to', 'confirmation_sent', 'created_at')
    list_filter   = ('status', 'meeting_type', 'assigned_to', 'date', 'confirmation_sent')
    search_fields = ('name', 'email', 'phone', 'company', 'service', 'message')
    list_editable = ('assigned_to',)
    list_display_links = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    actions       = ['confirm_appointments', 'cancel_appointments',
                     'send_confirmation_emails', 'resend_confirmation_email', 'mark_completed']

    fieldsets = (
        ('👤 Client Info', {
            'fields': ('name', 'email', 'phone', 'company'),
        }),
        ('📅 Schedule', {
            'fields': ('date', 'time', 'duration', 'meeting_type', 'meeting_link'),
        }),
        ('📋 Details', {
            'fields': ('service', 'message'),
        }),
        ('📊 Status & Assignment', {
            'fields': ('status', 'assigned_to', 'confirmation_sent', 'reminder_sent'),
        }),
        ('🔗 CRM Links', {
            'fields': ('lead', 'client'),
        }),
        ('📝 Internal Notes', {
            'fields': ('internal_notes',),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def date_time_display(self, obj):
        return format_html('<strong>{}</strong> at <strong>{}</strong> <small>({} min)</small>',
                           obj.date.strftime('%d %b %Y'),
                           obj.time.strftime('%I:%M %p'),
                           obj.duration)
    date_time_display.short_description = 'Date & Time'
    date_time_display.admin_order_field = 'date'

    def meeting_type_badge(self, obj):
        icons = {'zoom': '🎥', 'meet': '📹', 'phone': '📞', 'in_person': '🤝'}
        icon = icons.get(obj.meeting_type, '📅')
        link_html = ''
        if obj.meeting_link and obj.meeting_type in ('zoom', 'meet'):
            link_html = format_html(' <a href="{}" target="_blank">🔗 Join</a>', obj.meeting_link)
        return format_html('{} {}{}', icon, obj.get_meeting_type_display(), link_html)
    meeting_type_badge.short_description = 'Meeting'

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b', 'confirmed': '#10b981', 'cancelled': '#ef4444',
            'completed': '#6366f1', 'no_show': '#6b7280',
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{}</span>',
            colors.get(obj.status, '#6b7280'), obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def confirm_appointments(self, request, queryset):
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings as dj_settings

        confirmed_count = 0
        email_count = 0
        site_url = getattr(dj_settings, 'SITE_URL', '')

        for appt in queryset.filter(status='pending'):
            # 1. Status update karo
            appt.status = 'confirmed'
            appt.save(update_fields=['status'])
            confirmed_count += 1

            # 2. Auto-send confirmation HTML email (agar abhi tak nahi bheja)
            if not appt.confirmation_sent and appt.email:
                try:
                    html_body = render_to_string('website/email_appointment_confirm.html', {
                        'name':          appt.name,
                        'email':         appt.email,
                        'service':       appt.service,
                        'date':          appt.date.strftime('%d %b %Y'),
                        'time':          appt.time.strftime('%I:%M %p'),
                        'meeting_type':  appt.get_meeting_type_display(),
                        'meeting_link':  appt.meeting_link,
                        'site_name':     dj_settings.SITE_NAME,
                        'site_url':      site_url,
                        'support_email': dj_settings.DEFAULT_FROM_EMAIL,
                        'is_confirmed':  True,
                    })
                    plain_body = (
                        f'Dear {appt.name},\n\n'
                        f'Great news! Your appointment is CONFIRMED.\n\n'
                        f'Date    : {appt.date.strftime("%d %b %Y")}\n'
                        f'Time    : {appt.time.strftime("%I:%M %p")}\n'
                        f'Meeting : {appt.get_meeting_type_display()}\n'
                    )
                    if appt.meeting_link:
                        plain_body += f'Link    : {appt.meeting_link}\n'
                    plain_body += f'\nRegards,\n{dj_settings.SITE_NAME}'

                    msg = EmailMultiAlternatives(
                        subject    = f'✅ Appointment Confirmed — {appt.date.strftime("%d %b %Y")} | {dj_settings.SITE_NAME}',
                        body       = plain_body,
                        from_email = dj_settings.DEFAULT_FROM_EMAIL,
                        to         = [appt.email],
                    )
                    msg.attach_alternative(html_body, 'text/html')
                    msg.send(fail_silently=False)

                    appt.confirmation_sent = True
                    appt.save(update_fields=['confirmation_sent'])
                    email_count += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f'⚠️ Email failed for {appt.email}: {e}',
                        level='warning'
                    )

        if confirmed_count:
            self.message_user(
                request,
                f'✅ {confirmed_count} appointment(s) confirmed, {email_count} confirmation email(s) sent.'
            )
        else:
            self.message_user(request, 'ℹ️ No pending appointments found to confirm.', level='warning')
    confirm_appointments.short_description = '✅ Confirm & send confirmation email'

    def cancel_appointments(self, request, queryset):
        updated = queryset.exclude(status__in=['completed', 'cancelled']).update(status='cancelled')
        self.message_user(request, f'❌ {updated} appointment(s) cancelled.')
    cancel_appointments.short_description = '❌ Cancel selected appointments'

    def mark_completed(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='completed')
        self.message_user(request, f'🎉 {updated} appointment(s) marked as completed.')
    mark_completed.short_description = '🎉 Mark as Completed'

    def send_confirmation_emails(self, request, queryset):
        """
        Send HTML confirmation emails for confirmed appointments.
        Includes meeting_link if set.
        """
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings
        sent = 0
        site_url = getattr(settings, 'SITE_URL', '')
        for appt in queryset.filter(status='confirmed'):
            try:
                html_body = render_to_string('website/email_appointment_confirm.html', {
                    'name': appt.name,
                    'email': appt.email,
                    'service': appt.service,
                    'date': appt.date.strftime('%d %b %Y'),
                    'time': appt.time.strftime('%I:%M %p'),
                    'meeting_type': appt.get_meeting_type_display(),
                    'meeting_link': appt.meeting_link,
                    'site_name': settings.SITE_NAME,
                    'site_url': site_url,
                    'support_email': settings.DEFAULT_FROM_EMAIL,
                    'is_confirmed': True,
                })
                plain_body = (
                    f"Dear {appt.name},\n\nYour appointment is CONFIRMED!\n\n"
                    f"Date: {appt.date.strftime('%d %b %Y')}\n"
                    f"Time: {appt.time.strftime('%I:%M %p')}\n"
                    f"Meeting: {appt.get_meeting_type_display()}\n"
                )
                if appt.meeting_link:
                    plain_body += f"Link: {appt.meeting_link}\n"
                plain_body += f"\nThank you!\n{settings.SITE_NAME}"

                msg = EmailMultiAlternatives(
                    subject=f'✅ Appointment Confirmed — {appt.date.strftime("%d %b %Y")}',
                    body=plain_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[appt.email],
                )
                msg.attach_alternative(html_body, 'text/html')
                msg.send(fail_silently=False)
                appt.confirmation_sent = True
                appt.save(update_fields=['confirmation_sent'])
                sent += 1
            except Exception as e:
                self.message_user(request, f'⚠️ Failed for {appt.email}: {e}', level='warning')
        self.message_user(request, f'📧 Confirmation sent for {sent} appointment(s).')
    send_confirmation_emails.short_description = '📧 Send confirmation emails'

    def resend_confirmation_email(self, request, queryset):
        """
        Force-resend confirmation email for ANY confirmed appointment —
        ignores confirmation_sent flag. Use this after adding/updating meeting_link.
        """
        sent = skipped = 0
        for appt in queryset:
            if appt.status != 'confirmed':
                skipped += 1
                continue
            try:
                from django.core.mail import EmailMultiAlternatives
                from django.template.loader import render_to_string
                from django.conf import settings
                from .models import SiteSettings
                site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
                ss = SiteSettings.objects.first()
                support_email = ss.email if (ss and ss.email) else settings.DEFAULT_FROM_EMAIL
                meeting_labels = {
                    'zoom': 'Zoom Video Call', 'meet': 'Google Meet',
                    'phone': 'Phone Call', 'in_person': 'In Person',
                }
                meeting_display = meeting_labels.get(
                    appt.meeting_type,
                    appt.meeting_type.replace('_', ' ').title()
                )
                html_body = render_to_string('website/email_appointment_confirm.html', {
                    'name':          appt.name,
                    'email':         appt.email,
                    'service':       appt.service or 'General Consultation',
                    'date':          appt.date.strftime('%d %b %Y'),
                    'time':          appt.time.strftime('%I:%M %p'),
                    'meeting_type':  meeting_display,
                    'meeting_link':  appt.meeting_link or None,
                    'site_name':     settings.SITE_NAME,
                    'site_url':      site_url,
                    'support_email': support_email,
                    'is_confirmed':  True,
                })
                plain_body = (
                    f'Dear {appt.name},\n\n'
                    f'Your consultation with {settings.SITE_NAME} is CONFIRMED.\n\n'
                    f'Date    : {appt.date.strftime("%d %b %Y")}\n'
                    f'Time    : {appt.time.strftime("%I:%M %p")}\n'
                    f'Meeting : {meeting_display}\n'
                )
                if appt.meeting_link:
                    plain_body += f'Link    : {appt.meeting_link}\n'
                plain_body += f'\nWe look forward to speaking with you!\n\nRegards,\n{settings.SITE_NAME}'

                msg = EmailMultiAlternatives(
                    subject    = f'✅ Appointment Confirmed — {settings.SITE_NAME}',
                    body       = plain_body,
                    from_email = settings.DEFAULT_FROM_EMAIL,
                    to         = [appt.email],
                )
                msg.attach_alternative(html_body, 'text/html')
                msg.send(fail_silently=False)
                appt.confirmation_sent = True
                appt.save(update_fields=['confirmation_sent'])
                sent += 1
            except Exception as e:
                self.message_user(request, f'⚠️ Failed for {appt.email}: {e}', level='warning')

        msg_parts = []
        if sent:
            msg_parts.append(f'📧 Confirmation (re)sent to {sent} client(s).')
        if skipped:
            msg_parts.append(f'⚠️ {skipped} skipped (not confirmed).')
        self.message_user(request, ' '.join(msg_parts) or 'Nothing to do.')
    resend_confirmation_email.short_description = '🔄 Resend confirmation email (force — ignores sent flag)'


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░  ✍️ BLOG SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug', 'is_active', 'post_count')
    list_editable = ('is_active',)
    list_display_links = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        count = obj.posts.filter(status='published').count()
        return format_html('<strong>{}</strong> posts', count)
    post_count.short_description = 'Published Posts'


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug', 'post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'author', 'status_badge', 'is_featured',
                     'views', 'published_at', 'cover_preview')
    list_filter   = ('status', 'category', 'is_featured', 'published_at')
    search_fields = ('title', 'slug', 'excerpt', 'content', 'author',
                     'meta_title', 'meta_keywords')
    list_editable = ('is_featured',)
    list_display_links = ('title',)
    readonly_fields = ('views', 'created_at', 'updated_at', 'cover_preview', 'og_preview')
    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    actions       = ['publish_posts', 'draft_posts', 'archive_posts', 'mark_featured']

    fieldsets = (
        ('📝 Content', {
            'fields': ('title', 'slug', 'author', 'category', 'tags',
                       'excerpt', 'content', 'cover_image', 'cover_preview'),
        }),
        ('📊 Publishing', {
            'fields': ('status', 'is_featured', 'published_at'),
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords',
                       'canonical_url', 'og_image', 'og_preview'),
            'classes': ('collapse',),
            'description': '💡 meta_title ≤ 60 chars | meta_description ≤ 160 chars',
        }),
        ('📈 Stats', {
            'fields': ('views',),
            'classes': ('collapse',),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {'draft': '#f59e0b', 'published': '#10b981', 'archived': '#6b7280'}
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{}</span>',
            colors.get(obj.status, '#6b7280'), obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height:100px;border-radius:6px;" />', obj.cover_image.url)
        return '-'
    cover_preview.short_description = 'Cover Preview'

    def og_preview(self, obj):
        if obj.og_image:
            return format_html('<img src="{}" style="max-height:80px;border-radius:6px;" />', obj.og_image.url)
        return '-'
    og_preview.short_description = 'OG Image Preview'

    def publish_posts(self, request, queryset):
        updated = queryset.exclude(status='published').update(
            status='published', published_at=timezone.now()
        )
        self.message_user(request, f'✅ {updated} post(s) published.')
    publish_posts.short_description = '✅ Publish selected posts'

    def draft_posts(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'✏️ {updated} post(s) moved to draft.')
    draft_posts.short_description = '✏️ Move to Draft'

    def archive_posts(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'📦 {updated} post(s) archived.')
    archive_posts.short_description = '📦 Archive selected posts'

    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'⭐ {updated} post(s) marked as featured.')
    mark_featured.short_description = '⭐ Mark as Featured'


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░  🎁 GROWTH SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

class CouponUsageInline(admin.TabularInline):
    model           = CouponUsage
    extra           = 0
    readonly_fields = ('name', 'email', 'phone', 'order_value', 'discount_applied', 'used_at')
    can_delete      = False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display  = ('code', 'discount_display', 'discount_type', 'used_count',
                     'max_uses', 'valid_from', 'valid_until', 'is_active', 'validity_badge')
    list_editable = ('is_active',)
    list_display_links = ('code',)
    search_fields = ('code', 'description')
    list_filter   = ('discount_type', 'is_active')
    readonly_fields = ('used_count', 'created_at')
    inlines       = [CouponUsageInline]

    fieldsets = (
        ('🎟️ Coupon Details', {
            'fields': ('code', 'description', 'is_active'),
        }),
        ('💸 Discount', {
            'fields': ('discount_type', 'discount_value', 'min_order_value'),
        }),
        ('⏱️ Validity', {
            'fields': ('valid_from', 'valid_until', 'max_uses', 'used_count'),
        }),
        ('🕒 Created', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def discount_display(self, obj):
        if obj.discount_type == 'percent':
            return f'{obj.discount_value}%'
        return f'₹{obj.discount_value}'
    discount_display.short_description = 'Discount'

    def validity_badge(self, obj):
        is_valid, msg = obj.is_valid()
        if is_valid:
            return mark_safe('<span style="color:green;font-weight:600;">✓ Valid</span>')
        return format_html('<span style="color:red;">{}</span>', msg)
    validity_badge.short_description = 'Validity'


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display  = ('coupon', 'name', 'email', 'order_value', 'discount_applied', 'used_at')
    search_fields = ('coupon__code', 'name', 'email')
    list_filter   = ('coupon',)
    readonly_fields = ('used_at',)
    ordering      = ('-used_at',)


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display  = ('referrer_name', 'referrer_email', 'referral_code', 'status',
                     'referred_name', 'reward_given', 'created_at', 'link_display')
    list_editable = ('status', 'reward_given')
    list_display_links = ('referrer_name',)
    search_fields = ('referrer_name', 'referrer_email', 'referral_code', 'referred_name')
    list_filter   = ('status', 'reward_given')
    readonly_fields = ('referral_code', 'created_at', 'converted_at', 'link_display')

    fieldsets = (
        ('👤 Referrer', {
            'fields': ('referrer_name', 'referrer_email', 'referrer_phone',
                       'referral_code', 'link_display'),
        }),
        ('🤝 Referred', {
            'fields': ('referred_name', 'referred_email', 'referred_phone'),
        }),
        ('🎁 Reward', {
            'fields': ('status', 'reward_description', 'reward_given',
                       'created_at', 'converted_at'),
        }),
    )

    def link_display(self, obj):
        link = obj.referral_link()
        return format_html('<a href="{0}" target="_blank">{0}</a>', link)
    link_display.short_description = 'Referral Link'


class AffiliateClickInline(admin.TabularInline):
    model           = AffiliateClick
    extra           = 0
    readonly_fields = ('ip_address', 'landing_page', 'clicked_at')
    can_delete      = False
    max_num         = 20


class AffiliateConversionInline(admin.TabularInline):
    model           = AffiliateConversion
    extra           = 0
    readonly_fields = ('name', 'email', 'project', 'order_value', 'commission', 'status', 'created_at')
    can_delete      = False


@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'affiliate_code', 'commission_percent', 'status_badge',
                     'total_clicks', 'total_leads', 'total_converted',
                     'earned_display', 'pending_payout_display')
    list_editable = ('commission_percent',)
    list_display_links = ('name',)
    search_fields = ('name', 'email', 'affiliate_code', 'company')
    list_filter   = ('status',)
    readonly_fields = ('affiliate_code', 'total_clicks', 'total_leads',
                       'total_converted', 'total_earned', 'total_paid_out',
                       'created_at', 'affiliate_link_display')
    inlines       = [AffiliateClickInline, AffiliateConversionInline]

    fieldsets = (
        ('👤 Affiliate Info', {
            'fields': ('name', 'email', 'phone', 'company', 'website', 'how_promote'),
        }),
        ('🔗 Code & Link', {
            'fields': ('affiliate_code', 'affiliate_link_display', 'commission_percent'),
        }),
        ('📊 Stats', {
            'fields': ('status', 'total_clicks', 'total_leads',
                       'total_converted', 'total_earned', 'total_paid_out'),
        }),
        ('📝 Notes', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {'pending': '#f59e0b', 'active': '#10b981', 'suspended': '#ef4444'}
        return format_html(
            '<span style="color:{};font-weight:700;">{}</span>',
            colors.get(obj.status, '#6b7280'), obj.status.title()
        )
    status_badge.short_description = 'Status'

    def earned_display(self, obj):
        return format_html('<span style="color:#10b981;font-weight:700;">₹{}</span>', obj.total_earned)
    earned_display.short_description = 'Earned'

    def pending_payout_display(self, obj):
        color = '#ef4444' if obj.pending_payout > 0 else '#6b7280'
        return format_html('<span style="color:{};">₹{}</span>', color, obj.pending_payout)
    pending_payout_display.short_description = 'Pending Payout'

    def affiliate_link_display(self, obj):
        link = f'/go/{obj.affiliate_code}/'
        return format_html('<a href="{0}" target="_blank">{0}</a>', link)
    affiliate_link_display.short_description = 'Affiliate Link'

    actions = ['approve_affiliates', 'suspend_affiliates']

    def approve_affiliates(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='active')
        self.message_user(request, f'✅ {updated} affiliate(s) approved.')
    approve_affiliates.short_description = '✅ Approve selected affiliates'

    def suspend_affiliates(self, request, queryset):
        updated = queryset.exclude(status='suspended').update(status='suspended')
        self.message_user(request, f'🚫 {updated} affiliate(s) suspended.')
    suspend_affiliates.short_description = '🚫 Suspend selected affiliates'


@admin.register(AffiliateConversion)
class AffiliateConversionAdmin(admin.ModelAdmin):
    list_display  = ('affiliate', 'name', 'email', 'order_value', 'commission', 'status', 'created_at')
    list_editable = ('status',)
    list_display_links = ('name',)
    search_fields = ('name', 'email', 'affiliate__affiliate_code')
    list_filter   = ('status', 'affiliate')
    readonly_fields = ('commission', 'created_at')
    ordering      = ('-created_at',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == 'paid':
            aff = obj.affiliate
            aff.total_paid_out = sum(
                c.commission for c in AffiliateConversion.objects.filter(
                    affiliate=aff, status='paid'
                )
            )
            aff.save(update_fields=['total_paid_out'])


# ══════════════════════════════════════════════════════════════════
# ░░░░░░░░░░░░  🌐 WEBSITE SECTION  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ══════════════════════════════════════════════════════════════════

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display  = ('heading', 'is_active', 'order', 'button1_text', 'button2_text')
    list_editable = ('is_active', 'order')
    list_display_links = ('heading',)
    search_fields = ('heading', 'subheading', 'description')
    list_filter   = ('is_active',)
    readonly_fields = ('cover_preview',)

    def cover_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:120px;" />', obj.image.url)
        return '-'
    cover_preview.short_description = 'Image Preview'


@admin.register(TrustedClient)
class TrustedClientAdmin(admin.ModelAdmin):
    list_display  = ('name', 'is_active', 'order', 'logo_preview')
    list_editable = ('is_active', 'order')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter   = ('is_active',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height:60px;" />', obj.logo.url)
        return '-'
    logo_preview.short_description = 'Logo'


@admin.register(WhyChooseUs)
class WhyChooseUsAdmin(admin.ModelAdmin):
    list_display  = ('title', 'icon', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_display_links = ('title',)
    search_fields = ('title', 'description')
    list_filter   = ('is_active',)


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display  = ('step_number', 'title', 'icon', 'is_active')
    list_editable = ('is_active',)
    list_display_links = ('title',)
    search_fields = ('title', 'description')
    list_filter   = ('is_active',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ('client_name', 'company', 'role', 'is_active', 'order', 'img_preview')
    list_editable = ('is_active', 'order')
    list_display_links = ('client_name',)
    search_fields = ('client_name', 'company', 'role', 'feedback')
    list_filter   = ('is_active',)
    readonly_fields = ('img_preview',)

    def img_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;" />', obj.image.url)
        return '-'
    img_preview.short_description = 'Photo'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ('title', 'icon', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_display_links = ('title',)
    search_fields = ('title', 'description')
    list_filter   = ('is_active',)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display  = ('title', 'project_link', 'is_active', 'order', 'img_preview')
    list_editable = ('is_active', 'order')
    list_display_links = ('title',)
    search_fields = ('title', 'description')
    list_filter   = ('is_active',)
    readonly_fields = ('img_preview',)

    def img_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px;" />', obj.image.url)
        return '-'
    img_preview.short_description = 'Preview'


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display  = ('plan_name', 'price', 'is_popular', 'is_active', 'order')
    list_editable = ('is_popular', 'is_active', 'order')
    list_display_links = ('plan_name',)
    search_fields = ('plan_name', 'features')
    list_filter   = ('is_popular', 'is_active')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display  = ('question', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_display_links = ('question',)
    search_fields = ('question', 'answer')
    list_filter   = ('is_active',)


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display  = ('platform', 'url', 'is_active')
    list_editable = ('url', 'is_active')
    list_display_links = ('platform',)
    ordering      = ('platform',)


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('page', 'title')
    search_fields = ('title', 'content')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('🏢 Brand', {
            'fields': ('site_name', 'logo', 'meta_description'),
        }),
        ('📞 Contact Info', {
            'fields': (
                'email', 'contact_emails',
                'phone', 'contact_phones',
                'whatsapp', 'contact_whatsapps',
                'address',
            ),
            'description': mark_safe(
                '<div style="background:#e8f4fd;padding:10px 14px;border-radius:8px;'
                'border-left:4px solid #3b82f6;font-size:13px;margin-bottom:8px;">'
                '📌 <strong>Primary fields</strong> (Email, Phone, WhatsApp) → footer + contact page.<br>'
                '📋 <strong>Extra fields</strong> (Contact emails / phones / whatsapps) → sirf contact page. '
                'Ek line = ek entry.'
                '</div>'
            ),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change',
                    args=[obj.pk])
        )

    def response_change(self, request, obj):
        dj_messages.success(request, '✅ Site settings saved.')
        return super().response_change(request, obj)


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('🌐 Site Status', {
            'fields': ('site_online',),
            'description': (
                '<div style="background:#fff3cd;padding:10px 14px;border-radius:8px;'
                'border-left:4px solid #ffc107;font-size:13px;">'
                '⚠️ <strong>Turning off "Site Online" puts the site in maintenance mode</strong> '
                '(except /admin/ and bypass IPs).</div>'
            ),
        }),
        ('🔔 Admin Notifications', {
            'fields': ('admin_notification_emails',),
            'description': mark_safe(
                '<div style="background:#e8f4fd;padding:10px 14px;border-radius:8px;'
                'border-left:4px solid #3b82f6;font-size:13px;margin-bottom:8px;">'
                '📧 Yeh log <strong>new lead, contact form, aur appointment alerts</strong> receive karenge.<br>'
                'Comma separated likho — e.g. <code>owner@example.com, sales@example.com</code><br>'
                'Agar blank chhod do toh <code>DEFAULT_FROM_EMAIL</code> use hoga (settings.py se).'
                '</div>'
            ),
        }),
        ('🔧 Maintenance Page', {
            'fields': ('maintenance_title', 'maintenance_message',
                       'maintenance_email', 'maintenance_eta', 'bypass_ips'),
            'classes': ('collapse',),
        }),
        ('📄 Page Visibility', {
            'fields': ('page_home_active', 'page_services_active', 'page_portfolio_active',
                       'page_about_active', 'page_contact_active', 'page_coupons_active',
                       'page_referral_active', 'page_affiliate_active', 'page_blog_active'),
            'classes': ('collapse',),
        }),
        ('🧩 Home Page Sections', {
            'fields': ('section_hero_active', 'section_trusted_active', 'section_services_active',
                       'section_why_choose_active', 'section_process_active',
                       'section_portfolio_active', 'section_testimonials_active',
                       'section_pricing_active', 'section_faq_active',
                       'section_contact_active', 'section_chatbot_active'),
            'classes': ('collapse',),
        }),
        ('⚡ Features', {
            'fields': ('feature_coupons_active', 'feature_referral_active',
                       'feature_affiliate_active', 'feature_ai_chat_active'),
            'classes': ('collapse',),
        }),
        ('ℹ️ Info', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        return not GlobalSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = GlobalSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change',
                    args=[obj.pk])
        )

    def response_change(self, request, obj):
        dj_messages.success(request, '✅ Global settings saved.')
        return super().response_change(request, obj)


# ── Keep Hero registered (legacy) ──────────────────────────────
admin.site.register(Hero)


# ══════════════════════════════════════════════════════════════════
# PROXY MODEL IMPORTS — Jazzmin sidebar sections ke liye
# ══════════════════════════════════════════════════════════════════
from .models import (
    ContactProxy, ContactLeadProxy,
    LeadProxy, ClientProxy, ProjectProxy, CommunicationLogProxy, TaskProxy,
    PaymentOrderProxy, InvoiceProxy,
    ChatSessionProxy, ChatMessageProxy,
    EmailTemplateProxy, EmailLogProxy, NewsletterSubscriberProxy,
    AppointmentProxy,
    BlogPostProxy, BlogCategoryProxy, BlogTagProxy,
    CouponProxy, CouponUsageProxy, ReferralProxy,
    AffiliateProxy, AffiliateConversionProxy,
)


# ══════════════════════════════════════════════════════════════════
# 📞 CONTACTS SECTION
# ══════════════════════════════════════════════════════════════════

@admin.register(ContactProxy)
class ContactProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'email', 'phone', 'service', 'budget', 'created_at')
    list_filter    = ('service', 'budget', 'created_at')
    search_fields  = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at',)
    ordering       = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(ContactLeadProxy)
class ContactLeadProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'email', 'phone', 'created_at')
    search_fields  = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
    ordering       = ('-created_at',)
    date_hierarchy = 'created_at'


# ══════════════════════════════════════════════════════════════════
# 👥 CRM SECTION
# ══════════════════════════════════════════════════════════════════

@admin.register(LeadProxy)
class LeadProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'email', 'phone', 'service', 'status', 'created_at')
    list_filter    = ('status', 'service', 'created_at')
    search_fields  = ('name', 'email', 'phone')
    ordering       = ('-created_at',)
    date_hierarchy = 'created_at'
    list_editable  = ('status',)
    list_display_links = ('name',)


@admin.register(ClientProxy)
class ClientProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'email', 'phone', 'company', 'created_at')
    search_fields  = ('name', 'email', 'phone', 'company')
    ordering       = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(ProjectProxy)
class ProjectProxyAdmin(admin.ModelAdmin):
    list_display   = ('title', 'client', 'status', 'start_date', 'deadline')
    list_filter    = ('status',)
    search_fields  = ('title', 'client__name')
    list_editable  = ('status',)
    list_display_links = ('title',)


@admin.register(CommunicationLogProxy)
class CommunicationLogProxyAdmin(admin.ModelAdmin):
    list_display   = ('client', 'comm_type', 'done_by', 'subject', 'comm_date')
    list_filter    = ('comm_type', 'follow_up_done', 'comm_date')
    search_fields  = ('subject', 'body')
    ordering       = ('-comm_date',)
class TaskProxyAdmin(admin.ModelAdmin):
    list_display   = ('title', 'assigned_to', 'due_date', 'priority', 'status')
    list_filter    = ('priority', 'status', 'due_date')
    search_fields  = ('title',)
    list_editable  = ('status', 'priority')
    list_display_links = ('title',)


# ══════════════════════════════════════════════════════════════════
# 💳 PAYMENTS SECTION
# ══════════════════════════════════════════════════════════════════

@admin.register(PaymentOrderProxy)
class PaymentOrderProxyAdmin(admin.ModelAdmin):
    list_display   = ('customer_name', 'customer_email', 'amount', 'status', 'created_at')
    list_filter    = ('status', 'created_at')
    search_fields  = ('customer_name', 'customer_email', 'razorpay_order_id')
    readonly_fields = ('created_at',)
    ordering       = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(InvoiceProxy)
class InvoiceProxyAdmin(admin.ModelAdmin):
    list_display   = ('invoice_number', 'client_name', 'client_email',
                      'total_amount', 'status', 'issue_date')
    list_filter    = ('status', 'issue_date')
    search_fields  = ('invoice_number', 'client_name', 'client_email')
    readonly_fields = ('created_at', 'updated_at')
    ordering       = ('-created_at',)
    date_hierarchy = 'issue_date'
    list_editable  = ('status',)
    list_display_links = ('invoice_number',)

    actions = ['generate_pdf', 'send_email']

    def generate_pdf(self, request, queryset):
        from .invoice_utils import generate_invoice_pdf
        count = 0
        for inv in queryset:
            generate_invoice_pdf(inv)
            count += 1
        self.message_user(request, f'✅ {count} invoice PDF(s) generated.')
    generate_pdf.short_description = '📄 Generate PDF'

    def send_email(self, request, queryset):
        from .invoice_utils import send_invoice_by_email
        count = 0
        for inv in queryset:
            try:
                send_invoice_by_email(inv)
                count += 1
            except Exception as e:
                self.message_user(request, f'❌ {inv.invoice_number}: {e}', level='error')
        if count:
            self.message_user(request, f'📧 {count} invoice(s) emailed.')
    send_email.short_description = '📧 Send via Email'


# ══════════════════════════════════════════════════════════════════
# 💬 CHAT SECTION
# ══════════════════════════════════════════════════════════════════

@admin.register(ChatSessionProxy)
class ChatSessionProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'mobile', 'email', 'flow_state', 'is_ended', 'created_at')
    list_filter    = ('flow_state', 'is_ended', 'created_at')
    search_fields  = ('name', 'mobile', 'email')
    readonly_fields = ('session_id', 'created_at', 'ended_at')
    ordering       = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(ChatMessageProxy)
class ChatMessageProxyAdmin(admin.ModelAdmin):
    list_display   = ('session', 'sender', 'is_resolved', 'created_at')
    list_filter    = ('sender', 'is_resolved', 'created_at')
    search_fields  = ('message',)
    ordering       = ('-created_at',)


# ══════════════════════════════════════════════════════════════════
# 📧 EMAIL SECTION
# ══════════════════════════════════════════════════════════════════

@admin.register(EmailTemplateProxy)
class EmailTemplateProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'subject', 'created_at')
    search_fields  = ('name', 'subject')
    ordering       = ('name',)


@admin.register(EmailLogProxy)
class EmailLogProxyAdmin(admin.ModelAdmin):
    list_display   = ('recipient', 'subject', 'status', 'sent_at')
    list_filter    = ('status', 'sent_at')
    search_fields  = ('recipient', 'subject')
    readonly_fields = ('sent_at',)
    ordering       = ('-sent_at',)
    date_hierarchy = 'sent_at'


@admin.register(NewsletterSubscriberProxy)
class NewsletterSubscriberProxyAdmin(admin.ModelAdmin):
    list_display   = ('email', 'subscribed_at', 'is_active')
    list_filter    = ('is_active', 'subscribed_at')
    search_fields  = ('email',)
    readonly_fields = ('subscribed_at',)
    ordering       = ('-subscribed_at',)




# ══════════════════════════════════════════════════════════════════
# 📅 APPOINTMENTS SECTION — FIXED WITH EMAIL AUTOMATION
# ══════════════════════════════════════════════════════════════════

@admin.register(AppointmentProxy)
class AppointmentProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'email', 'phone', 'service', 'date', 'time',
                      'meeting_type', 'status', 'status_badge', 'confirmation_badge')
    list_filter    = ('status', 'meeting_type', 'date', 'confirmation_sent')
    search_fields  = ('name', 'email', 'phone', 'company', 'service')
    list_editable  = ('status',)
    list_display_links = ('name',)
    ordering       = ('-date', '-time')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at', 'confirmation_sent')
    actions        = ['resend_confirmation_email']
    
    fieldsets = (
        ('👤 Client Info', {
            'fields': ('name', 'email', 'phone', 'company'),
        }),
        ('📅 Appointment Details', {
            'fields': ('service', 'date', 'time', 'duration', 'message'),
        }),
        ('🎥 Meeting', {
            'fields': ('meeting_type', 'meeting_link'),
        }),
        ('📊 Status & Assignment', {
            'fields': ('status', 'assigned_to', 'confirmation_sent'),
        }),
        ('🔗 CRM Links', {
            'fields': ('lead', 'client'),
            'classes': ('collapse',),
        }),
        ('📝 Internal Notes', {
            'fields': ('internal_notes',),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        """Display colorful status badge."""
        colors = {
            'pending':   '#f59e0b',  # orange
            'confirmed': '#10b981',  # green
            'cancelled': '#ef4444',  # red
            'completed': '#6366f1',  # indigo
            'no_show':   '#6b7280',  # gray
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 12px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def confirmation_badge(self, obj):
        """Show if confirmation email was sent."""
        if obj.confirmation_sent:
            return mark_safe('<span style="color:#10b981;font-weight:600;">✅ Sent</span>')
        return mark_safe('<span style="color:#94a3b8;">⏳ Pending</span>')
    confirmation_badge.short_description = 'Email'

    def save_model(self, request, obj, form, change):
        """
        Two triggers:
          1. Admin creates NEW appointment (change=False):
             - Send email immediately.
             - If status=confirmed (admin set it while creating): is_confirmed=True + meeting_link included.
             - If status=pending: is_confirmed=False (acknowledgement email).
          2. Admin EDITS existing appointment and status transitions to confirmed:
             - Send confirmation email with latest meeting_link.
        """
        old_status = None
        if change and obj.pk:
            try:
                from .models import Appointment as _Appt
                old_status = _Appt.objects.get(pk=obj.pk).status
            except Exception:
                pass

        super().save_model(request, obj, form, change)

        # ── Case 1: Brand new appointment created by admin ──────────────
        if not change:
            try:
                from django.core.mail import EmailMultiAlternatives
                from django.template.loader import render_to_string
                from django.conf import settings
                from .models import SiteSettings
                site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
                ss = SiteSettings.objects.first()
                support_email = ss.email if (ss and ss.email) else settings.DEFAULT_FROM_EMAIL
                meeting_labels = {
                    'zoom': 'Zoom Video Call', 'meet': 'Google Meet',
                    'phone': 'Phone Call', 'in_person': 'In Person',
                }
                meeting_display = meeting_labels.get(
                    obj.meeting_type,
                    obj.meeting_type.replace('_', ' ').title()
                )
                is_confirmed = obj.status == 'confirmed'
                html_body = render_to_string('website/email_appointment_confirm.html', {
                    'name':          obj.name,
                    'email':         obj.email,
                    'service':       obj.service or 'General Consultation',
                    'date':          obj.date.strftime('%d %b %Y'),
                    'time':          obj.time.strftime('%I:%M %p'),
                    'meeting_type':  meeting_display,
                    'meeting_link':  obj.meeting_link or None,
                    'site_name':     settings.SITE_NAME,
                    'site_url':      site_url,
                    'support_email': support_email,
                    'is_confirmed':  is_confirmed,
                })
                plain_body = (
                    f'Dear {obj.name},\n\n'
                    + (
                        f'Your consultation with {settings.SITE_NAME} is CONFIRMED.\n\n'
                        if is_confirmed else
                        f'Your consultation request has been scheduled.\n\n'
                    )
                    + f'Date    : {obj.date.strftime("%d %b %Y")}\n'
                    + f'Time    : {obj.time.strftime("%I:%M %p")}\n'
                    + f'Meeting : {meeting_display}\n'
                )
                if obj.meeting_link:
                    plain_body += f'Link    : {obj.meeting_link}\n'
                plain_body += f'\nWe look forward to speaking with you!\n\nRegards,\n{settings.SITE_NAME}'

                subject = (
                    f'✅ Appointment Confirmed — {settings.SITE_NAME}'
                    if is_confirmed
                    else f'📅 Appointment Scheduled — {settings.SITE_NAME}'
                )
                msg = EmailMultiAlternatives(
                    subject    = subject,
                    body       = plain_body,
                    from_email = settings.DEFAULT_FROM_EMAIL,
                    to         = [obj.email],
                )
                msg.attach_alternative(html_body, 'text/html')
                msg.send(fail_silently=False)

                if is_confirmed:
                    obj.confirmation_sent = True
                    obj.save(update_fields=['confirmation_sent'])

                dj_messages.success(
                    request,
                    f'✅ {"Confirmation" if is_confirmed else "Acknowledgement"} email sent to {obj.email}'
                )
            except Exception as e:
                dj_messages.warning(
                    request,
                    f'⚠️ Could not send email to {obj.email}: {e}'
                )
            return

        # ── Case 2: Status just changed TO 'confirmed' ──────────────────
        if (
            change
            and old_status is not None
            and old_status != 'confirmed'
            and obj.status == 'confirmed'
        ):
            success = self._send_confirmation_email(obj)

            if success:
                obj.confirmation_sent = True
                obj.save(update_fields=['confirmation_sent'])
                dj_messages.success(
                    request,
                    f'✅ Confirmation email sent to {obj.email}'
                )
            else:
                dj_messages.warning(
                    request,
                    f'⚠️ Failed to send confirmation email to {obj.email}. '
                    f'Check your email settings and server logs.'
                )

    def _send_confirmation_email(self, appointment):
        """
        Send HTML confirmation email to the user.
        Returns True if successful, False otherwise.
        """
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Get site settings for support email
            site_settings = SiteSettings.objects.first()
            support_email = (
                site_settings.email 
                if site_settings and site_settings.email 
                else settings.DEFAULT_FROM_EMAIL
            )
            site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
            
            # Meeting type display labels
            meeting_labels = {
                'zoom': 'Zoom Video Call',
                'meet': 'Google Meet',
                'phone': 'Phone Call',
                'in_person': 'In Person',
            }
            meeting_display = meeting_labels.get(
                appointment.meeting_type,
                appointment.meeting_type.replace('_', ' ').title()
            )
            
            # Render HTML email template
            html_body = render_to_string('website/email_appointment_confirm.html', {
                'name':          appointment.name,
                'email':         appointment.email,
                'service':       appointment.service or 'General Consultation',
                'date':          appointment.date.strftime('%d %b %Y'),
                'time':          appointment.time.strftime('%I:%M %p'),
                'meeting_type':  meeting_display,
                'meeting_link':  appointment.meeting_link or None,
                'site_name':     settings.SITE_NAME,
                'site_url':      site_url,
                'support_email': support_email,
                'is_confirmed':  True,  # ✅ This is the confirmed email
            })
            
            # Plain text fallback body
            plain_body = (
                f'Dear {appointment.name},\n\n'
                f'Great news! Your consultation with {settings.SITE_NAME} '
                f'is now CONFIRMED.\n\n'
                f'📅 Date: {appointment.date.strftime("%d %b %Y")}\n'
                f'🕐 Time: {appointment.time.strftime("%I:%M %p")}\n'
                f'📹 Meeting: {meeting_display}\n'
            )
            
            if appointment.meeting_link:
                plain_body += f'\n🔗 Join Link: {appointment.meeting_link}\n'
            
            plain_body += (
                f'\n\nPlease add this to your calendar and join a few minutes early.\n'
                f'We look forward to speaking with you!\n\n'
                f'Best regards,\n{settings.SITE_NAME}\n'
                f'{support_email}'
            )
            
            # Create and send email
            msg = EmailMultiAlternatives(
                subject    = f'✅ Appointment Confirmed — {settings.SITE_NAME}',
                body       = plain_body,
                from_email = settings.DEFAULT_FROM_EMAIL,
                to         = [appointment.email],
            )
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=False)  # Raise exception if fails
            
            logger.info(
                f'✅ Confirmation email sent successfully to {appointment.email} '
                f'for appointment on {appointment.date}'
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f'❌ Failed to send confirmation email to {appointment.email}: {str(e)}',
                exc_info=True  # This will log the full traceback
            )
            return False

    def resend_confirmation_email(self, request, queryset):
        """
        Force-resend confirmation email — ignores confirmation_sent flag.
        Use this after updating meeting_link on an already-confirmed appointment.
        Works for confirmed appointments only.
        """
        sent = skipped = 0
        for appt in queryset:
            if appt.status != 'confirmed':
                skipped += 1
                continue
            success = self._send_confirmation_email(appt)
            if success:
                appt.confirmation_sent = True
                appt.save(update_fields=['confirmation_sent'])
                sent += 1
            else:
                self.message_user(
                    request,
                    f'⚠️ Email failed for {appt.email}. Check server logs.',
                    level='warning'
                )
        parts = []
        if sent:
            parts.append(f'📧 Confirmation email (re)sent to {sent} client(s).')
        if skipped:
            parts.append(f'⚠️ {skipped} skipped — not confirmed yet.')
        self.message_user(request, ' '.join(parts) or 'Nothing to do.')
    resend_confirmation_email.short_description = '🔄 Resend confirmation email (force — ignores sent flag)'

# ══════════════════════════════════════════════════════════════════
# ✍️ BLOG SECTION
# ══════════════════════════════════════════════════════════════════

@admin.register(BlogPostProxy)
class BlogPostProxyAdmin(admin.ModelAdmin):
    list_display   = ('title', 'category', 'status', 'is_featured',
                      'views', 'published_at')
    list_filter    = ('status', 'is_featured', 'category', 'published_at')
    search_fields  = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable  = ('status', 'is_featured')
    list_display_links = ('title',)
    ordering       = ('-published_at', '-created_at')
    date_hierarchy = 'published_at'
    filter_horizontal = ('tags',)


@admin.register(BlogCategoryProxy)
class BlogCategoryProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'slug', 'is_active')
    list_editable  = ('is_active',)
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields  = ('name',)


@admin.register(BlogTagProxy)
class BlogTagProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields  = ('name',)


# ══════════════════════════════════════════════════════════════════
# 🎁 GROWTH SECTION
# ══════════════════════════════════════════════════════════════════

@admin.register(CouponProxy)
class CouponProxyAdmin(admin.ModelAdmin):
    list_display   = ('code', 'discount_type', 'discount_value',
                      'used_count', 'max_uses', 'is_active', 'valid_until')
    list_filter    = ('discount_type', 'is_active')
    search_fields  = ('code', 'description')
    list_editable  = ('is_active',)
    list_display_links = ('code',)
    ordering       = ('-created_at',)


@admin.register(CouponUsageProxy)
class CouponUsageProxyAdmin(admin.ModelAdmin):
    list_display   = ('coupon', 'name', 'email', 'order_value',
                      'discount_applied', 'used_at')
    list_filter    = ('used_at',)
    search_fields  = ('name', 'email', 'coupon__code')
    readonly_fields = ('used_at',)
    ordering       = ('-used_at',)


@admin.register(ReferralProxy)
class ReferralProxyAdmin(admin.ModelAdmin):
    list_display   = ('referrer_name', 'referrer_email', 'referral_code',
                      'referred_name', 'status', 'status_badge', 'reward_badge', 'created_at')
    list_filter    = ('status', 'reward_given', 'created_at')
    search_fields  = ('referrer_name', 'referrer_email', 'referral_code',
                      'referred_name', 'referred_email')
    list_editable  = ('status',)
    list_display_links = ('referrer_name',)
    ordering       = ('-created_at',)
    readonly_fields = ('created_at', 'converted_at', 'referral_link_display')
    date_hierarchy  = 'created_at'
    actions         = ['mark_rewarded', 'mark_converted']

    fieldsets = (
        ('👤 Referrer', {
            'fields': ('referrer_name', 'referrer_email', 'referrer_phone'),
        }),
        ('🔗 Link', {
            'fields': ('referral_code', 'referral_link_display'),
        }),
        ('✅ Referred Person', {
            'fields': ('referred_name', 'referred_email', 'referred_phone'),
        }),
        ('🎁 Reward & Status', {
            'fields': ('status', 'reward_description', 'reward_given'),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'converted_at'),
            'classes': ('collapse',),
        }),
    )

    def referral_link_display(self, obj):
        link = obj.referral_link
        return format_html('<a href="{}" target="_blank">{}</a>', link, link)
    referral_link_display.short_description = 'Referral Link'

    def status_badge(self, obj):
        colours = {
            'pending':   '#f59e0b',
            'converted': '#3b82f6',
            'rewarded':  '#10b981',
        }
        c = colours.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;">{}</span>',
            c, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def reward_badge(self, obj):
        if obj.reward_given:
            return mark_safe('<span style="color:#10b981;font-weight:600;">✅ Given</span>')
        return mark_safe('<span style="color:#94a3b8;">Pending</span>')
    reward_badge.short_description = 'Reward'

    def mark_rewarded(self, request, queryset):
        """
        Admin action: approve reward for selected referrals.
        For each referral:
          1. Generate a unique coupon code (₹500 flat, 30-day expiry, single use)
          2. Send the coupon code to referrer's email
          3. Mark reward_given=True and status='rewarded'
        """
        from django.utils import timezone
        from datetime import timedelta
        import uuid
        from .models import Coupon
        from django.conf import settings
        from django.core.mail import EmailMultiAlternatives

        rewarded = 0
        for referral in queryset.filter(reward_given=False):
            try:
                # ── Step 1: Generate unique coupon ──────────────────
                coupon_code = f"REF-{referral.referral_code.upper()}"
                expiry_date = timezone.now() + timedelta(days=30)

                coupon, created = Coupon.objects.get_or_create(
                    code=coupon_code,
                    defaults={
                        'discount_type':  'flat',
                        'discount_value': 500,
                        'is_active':      True,
                        'valid_from':     timezone.now(),
                        'valid_until':    expiry_date,
                        'max_uses':       1,
                    }
                )

                # ── Step 2: Send coupon email to referrer ───────────
                site_url = getattr(settings, 'SITE_URL', '')
                try:
                    from .models import SiteSettings
                    ss = SiteSettings.objects.first()
                    site_name = ss.site_name if ss else 'NextZenDev'
                    support_email = ss.email if (ss and ss.email) else settings.DEFAULT_FROM_EMAIL
                except Exception:
                    site_name = 'NextZenDev'
                    support_email = settings.DEFAULT_FROM_EMAIL

                reward_desc = referral.reward_description or '₹500 discount on your next project'
                subject = f"🎁 Your Referral Reward is Here! — {site_name}"
                html = f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:32px;background:#f9fafb;border-radius:12px;">
                  <h2 style="color:#0f172a;">Congratulations, {referral.referrer_name}! 🎉</h2>
                  <p style="color:#475569;">
                    <strong>{referral.referred_name or 'Your friend'}</strong> signed up using your referral link.
                    Your reward coupon is ready!
                  </p>

                  <div style="background:#f0fdf4;border:2px dashed #4ade80;border-radius:12px;padding:24px;margin:24px 0;text-align:center;">
                    <p style="font-size:12px;color:#94a3b8;margin:0 0 8px;text-transform:uppercase;letter-spacing:.05em;">Your Coupon Code</p>
                    <p style="font-family:monospace;font-size:28px;font-weight:800;color:#15803d;letter-spacing:3px;margin:0 0 8px;">{coupon_code}</p>
                    <p style="color:#166534;font-size:13px;margin:0;">₹500 discount · Valid till {expiry_date.strftime('%d %b %Y')} · Single use</p>
                  </div>

                  <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px;margin:16px 0;">
                    <p style="color:#1e40af;font-weight:600;margin:0 0 6px;">How to use?</p>
                    <p style="color:#1e40af;font-size:13px;margin:0;">Apply this code at checkout on your next project with us. The ₹500 discount will be applied automatically.</p>
                  </div>

                  <p style="color:#475569;font-size:14px;">Questions? Contact us at <a href="mailto:{support_email}" style="color:#6366f1;">{support_email}</a></p>
                  <p style="color:#94a3b8;font-size:12px;margin-top:32px;">— The {site_name} Team</p>
                </div>
                """
                plain = (
                    f"Congratulations {referral.referrer_name}!\n\n"
                    f"{referral.referred_name or 'Your friend'} signed up using your referral link.\n\n"
                    f"Your Reward Coupon Code: {coupon_code}\n"
                    f"Discount: ₹500\n"
                    f"Valid till: {expiry_date.strftime('%d %b %Y')}\n"
                    f"Single use only\n\n"
                    f"Apply at checkout on your next project.\n\n"
                    f"— {site_name}"
                )
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[referral.referrer_email],
                )
                msg.attach_alternative(html, 'text/html')
                msg.send(fail_silently=True)

                # ── Step 3: Mark as rewarded ────────────────────────
                referral.reward_given = True
                referral.status = 'rewarded'
                referral.save(update_fields=['reward_given', 'status'])
                rewarded += 1

            except Exception as e:
                self.message_user(
                    request,
                    f'⚠️ Error processing reward for {referral.referrer_email}: {e}',
                    level='error'
                )

        if rewarded:
            self.message_user(
                request,
                f'✅ {rewarded} referral(s) rewarded — coupon codes generated and emailed to referrers.'
            )
    mark_rewarded.short_description = '🎁 Mark selected as Rewarded (auto-generate & email coupon)'

    def mark_converted(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='converted', converted_at=timezone.now()
        )
        self.message_user(request, f'🔄 {updated} referral(s) marked as converted.')
    mark_converted.short_description = '🔄 Mark selected as Converted'


@admin.register(AffiliateProxy)
class AffiliateProxyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'email', 'affiliate_code', 'commission_percent',
                      'status', 'status_badge', 'total_clicks', 'total_converted',
                      'total_earned', 'pending_payout_display', 'created_at')
    list_filter    = ('status', 'created_at')
    search_fields  = ('name', 'email', 'affiliate_code', 'company')
    list_editable  = ('status',)
    list_display_links = ('name',)
    ordering       = ('-created_at',)
    readonly_fields = ('created_at', 'total_clicks', 'total_leads',
                       'total_converted', 'total_earned', 'total_paid_out',
                       'affiliate_link_display')
    date_hierarchy  = 'created_at'
    actions         = ['approve_selected', 'suspend_selected']

    fieldsets = (
        ('👤 Affiliate Info', {
            'fields': ('name', 'email', 'phone', 'company', 'website'),
        }),
        ('📣 Promotion', {
            'fields': ('how_promote',),
        }),
        ('🔗 Affiliate Details', {
            'fields': ('affiliate_code', 'affiliate_link_display', 'commission_percent', 'status'),
        }),
        ('📊 Stats (auto-updated)', {
            'fields': ('total_clicks', 'total_leads', 'total_converted',
                       'total_earned', 'total_paid_out'),
        }),
        ('📝 Notes', {
            'fields': ('notes',),
        }),
        ('🕒 Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def affiliate_link_display(self, obj):
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
        link = f"{site_url}/aff/{obj.affiliate_code}/"
        return format_html('<a href="{}" target="_blank">{}</a>', link, link)
    affiliate_link_display.short_description = 'Affiliate Link'

    def status_badge(self, obj):
        colours = {
            'pending':   '#f59e0b',
            'active':    '#10b981',
            'suspended': '#ef4444',
        }
        c = colours.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;">{}</span>',
            c, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def pending_payout_display(self, obj):
        amount = obj.pending_payout
        if amount > 0:
            return format_html('<span style="color:#f59e0b;font-weight:600;">₹{}</span>', amount)
        return format_html('<span style="color:#94a3b8;">₹0</span>')
    pending_payout_display.short_description = 'Pending Payout'

    def approve_selected(self, request, queryset):
        """Approve pending affiliates — signals will send approval emails."""
        updated = queryset.filter(status='pending')
        count = 0
        for aff in updated:
            aff.status = 'active'
            aff.save()  # triggers signal → sends approval email
            count += 1
        self.message_user(request, f'✅ {count} affiliate(s) approved. Approval emails sent automatically.')
    approve_selected.short_description = '✅ Approve selected affiliates'

    def suspend_selected(self, request, queryset):
        count = 0
        for aff in queryset.filter(status='active'):
            aff.status = 'suspended'
            aff.save()  # triggers signal → sends suspension email
            count += 1
        self.message_user(request, f'⚠️ {count} affiliate(s) suspended.')
    suspend_selected.short_description = '⚠️ Suspend selected affiliates'


@admin.register(AffiliateConversionProxy)
class AffiliateConversionProxyAdmin(admin.ModelAdmin):
    list_display   = ('affiliate', 'name', 'email', 'status', 'status_badge',
                      'order_value', 'commission_display', 'created_at')
    list_filter    = ('status', 'created_at')
    search_fields  = ('name', 'email', 'affiliate__name', 'affiliate__affiliate_code')
    list_editable  = ('status',)
    list_display_links = ('affiliate',)
    ordering       = ('-created_at',)
    readonly_fields = ('commission', 'created_at')
    date_hierarchy  = 'created_at'
    actions         = ['mark_paid']

    fieldsets = (
        ('👤 Client', {
            'fields': ('affiliate', 'name', 'email', 'phone', 'project'),
        }),
        ('💰 Financials', {
            'fields': ('order_value', 'commission', 'status'),
        }),
        ('📝 Notes', {
            'fields': ('notes',),
        }),
        ('🕒 Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colours = {
            'lead':      '#6366f1',
            'converted': '#f59e0b',
            'paid':      '#10b981',
        }
        c = colours.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;">{}</span>',
            c, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def commission_display(self, obj):
        if obj.commission:
            return format_html('<span style="color:#15803d;font-weight:600;">₹{}</span>', obj.commission)
        return '—'
    commission_display.short_description = 'Commission'

    def mark_paid(self, request, queryset):
        """Mark conversions as paid — signal updates total_paid_out automatically."""
        count = 0
        for conv in queryset.filter(status='converted'):
            conv.status = 'paid'
            conv.save()  # triggers signal
            count += 1
        self.message_user(request, f'✅ {count} conversion(s) marked as paid. Affiliates notified.')
    mark_paid.short_description = '💰 Mark selected as Paid'