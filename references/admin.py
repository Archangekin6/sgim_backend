from django.contrib import admin
from . import models
from unfold.admin import ModelAdmin


class ReferenceAdminBase(ModelAdmin):
    list_display = ("name", "code", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    prepopulated_fields = {"code": ("name",)}


@admin.register(models.AlertSource)
class AlertSourceAdmin(ReferenceAdminBase):
    pass


@admin.register(models.Priority)
class PriorityAdmin(ReferenceAdminBase):
    list_display = ReferenceAdminBase.list_display + ("level",)


@admin.register(models.Severity)
class SeverityAdmin(ReferenceAdminBase):
    list_display = ReferenceAdminBase.list_display + ("level",)


@admin.register(models.VesselType)
class VesselTypeAdmin(ReferenceAdminBase):
    pass


@admin.register(models.IncidentCategory)
class IncidentCategoryAdmin(ReferenceAdminBase):
    pass


@admin.register(models.MeansCategory)
class MeansCategoryAdmin(ReferenceAdminBase):
    pass


@admin.register(models.MeansType)
class MeansTypeAdmin(ReferenceAdminBase):
    list_display = ReferenceAdminBase.list_display + ("category",)
    list_filter = ReferenceAdminBase.list_filter + ("category",)


@admin.register(models.PartnerType)
class PartnerTypeAdmin(ReferenceAdminBase):
    pass


@admin.register(models.PersonRole)
class PersonRoleAdmin(ReferenceAdminBase):
    pass


@admin.register(models.PersonStatus)
class PersonStatusAdmin(ReferenceAdminBase):
    pass