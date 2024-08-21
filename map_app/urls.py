# map_app/urls.py

from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("theme/create/", views.create_theme, name="create_theme"),
    path("theme/<int:theme_id>/", views.theme_detail, name="theme_detail"),
    path("theme/<int:theme_id>/upload/", views.upload_photo, name="upload_photo"),
    path("theme/<int:theme_id>/map/", views.view_map, name="view_map"),
    path("theme/<int:theme_id>/get_locations/", views.get_locations, name="get_locations"),
    path("photo/<int:photo_id>/delete/", views.delete_photo, name="delete_photo"),
    path("location/<int:location_id>/edit/", views.edit_location, name="edit_location"),
    path("location/<int:location_id>/delete/", views.delete_location, name="delete_location"),
]
