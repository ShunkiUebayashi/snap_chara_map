# map_app/admin.py

from django.contrib import admin

from .models import Location, Photo, Theme


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("name", "user__username")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "theme", "latitude", "longitude")
    list_filter = ("theme",)
    search_fields = ("name", "theme__name")


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("caption", "location", "theme", "user", "taken_at", "uploaded_at")
    list_filter = ("theme", "location", "user", "taken_at", "uploaded_at")
    search_fields = ("caption", "location__name", "theme__name", "user__username")
