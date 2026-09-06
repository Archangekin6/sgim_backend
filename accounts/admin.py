from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from unfold.admin import ModelAdmin
from .models import PasswordResetRequest


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    list_display = ("username", "get_full_name", "role", "team", "center", "is_active")
    list_filter = ("role", "team", "center", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("SGIM", {"fields": ("role", "team", "center", "phone")}),
    )   

@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(ModelAdmin):
    list_display = ("user", "status", "requested_at", "resolved_by", "resolved_at")
    list_filter = ("status",)