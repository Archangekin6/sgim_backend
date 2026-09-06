from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from unfold.admin import ModelAdmin
from .models import PasswordResetRequest

from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

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
    

class ResolvePasswordForm(forms.Form):
    new_password = forms.CharField(label="Nouveau mot de passe", widget=forms.PasswordInput)


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(ModelAdmin):
    list_display = ("user", "status", "requested_at", "resolved_by", "resolved_at", "action_resoudre")
    list_filter = ("status",)
    readonly_fields = ("user", "note", "status", "requested_at", "resolved_by", "resolved_at")

    def has_add_permission(self, request):
        return False

    def action_resoudre(self, obj):
        if obj.status == PasswordResetRequest.Status.PENDING:
            url = reverse("admin:accounts_passwordresetrequest_resolve", args=[obj.pk])
            return format_html('<a class="button" href="{}">Résoudre</a>', url)
        return "—"
    action_resoudre.short_description = "Action"

    def get_urls(self):
        custom = [
            path(
                "<uuid:pk>/resolve/",
                self.admin_site.admin_view(self.resolve_view),
                name="accounts_passwordresetrequest_resolve",
            ),
        ]
        return custom + super().get_urls()

    def resolve_view(self, request, pk):
        reset_request = get_object_or_404(PasswordResetRequest, pk=pk)

        if not (request.user.is_superuser or getattr(request.user, "role", None) in ("ADMIN", "SUPERADMIN")):
            messages.error(request, "Vous n'avez pas le droit de traiter cette demande.")
            return redirect("admin:accounts_passwordresetrequest_changelist")

        if request.method == "POST":
            form = ResolvePasswordForm(request.POST)
            if form.is_valid():
                reset_request.user.set_password(form.cleaned_data["new_password"])
                reset_request.user.save()
                reset_request.status = PasswordResetRequest.Status.RESOLVED
                reset_request.resolved_by = request.user
                reset_request.resolved_at = timezone.now()
                reset_request.save()
                messages.success(request, f"Mot de passe de {reset_request.user.username} réinitialisé.")
                return redirect("admin:accounts_passwordresetrequest_changelist")
        else:
            form = ResolvePasswordForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            reset_request=reset_request,
            title=f"Résoudre la demande de {reset_request.user.username}",
        )
        return render(request, "admin/accounts/resolve_password_request.html", context)