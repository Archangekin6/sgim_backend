from rest_framework.permissions import BasePermission


class IsAdminTier(BasePermission):
    """Admin et Super Admin uniquement (pas les comptes Car1-4/MRSC)."""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            (user.role in ("ADMIN", "SUPERADMIN") or user.is_superuser)
        )


class IsSuperAdmin(BasePermission):
    """Super Administrateur uniquement (ex: gestion des comptes)."""
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.role == "SUPERADMIN" or user.is_superuser))