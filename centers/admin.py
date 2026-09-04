from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Center

admin.site.register(Center)