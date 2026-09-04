from django.contrib import admin
from .models import Partner
from unfold.admin import ModelAdmin


@admin.register(Partner)
class PartnerAdmin(ModelAdmin):
    list_display = ("name", "partner_type", "phone", "email", "is_active")
    list_filter = ("partner_type", "is_active")
    search_fields = ("name", "email", "phone")