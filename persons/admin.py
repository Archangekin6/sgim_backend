from django.contrib import admin
from .models import Person
from unfold.admin import ModelAdmin


@admin.register(Person)
class PersonAdmin(ModelAdmin):
    list_display = ("name", "alert", "role", "status", "nationality")
    list_filter = ("role", "status")
    search_fields = ("name", "alert__number")