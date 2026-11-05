from rest_framework.permissions import BasePermission


class IsAdminTier(BasePermission):
    """Admin et Super Admin uniquement."""
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


class IsTeamLeader(BasePermission):
    """Chef de quart uniquement."""
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == "TEAM_LEADER")


class IsOperatorOrAbove(BasePermission):
    """Opérateur, Chef de quart, Admin et Super Admin."""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            (user.role in ("OPERATOR", "TEAM_LEADER", "ADMIN", "SUPERADMIN") or user.is_superuser)
        )
