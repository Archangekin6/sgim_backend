from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from unfold.admin import ModelAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    list_display = ("username", "get_full_name", "role", "team", "center", "is_active")
    list_filter = ("role", "team", "center", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("SGIM", {"fields": ("role", "team", "center", "phone")}),
    )