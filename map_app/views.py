# map_app/views.py
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Prefetch
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    LocationForm,
    LocationSelectionForm,
    NewLocationForm,
    PhotoForm,
    SignUpForm,
    ThemeForm,
)
from .models import Location, Photo, Theme


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def home(request):
    themes = Theme.objects.filter(user=request.user)
    return render(request, "home.html", {"themes": themes})


@login_required
def create_theme(request):
    if request.method == "POST":
        form = ThemeForm(request.POST)
        if form.is_valid():
            theme = form.save(commit=False)
            theme.user = request.user
            theme.save()
            return redirect("home")
    else:
        form = ThemeForm()
    return render(request, "theme/create.html", {"form": form})


@login_required
def upload_photo(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id, user=request.user)
    locations = Location.objects.filter(theme=theme)
    locations_json = json.dumps(
        [{"id": loc.id, "name": loc.name, "latitude": loc.latitude, "longitude": loc.longitude} for loc in locations]
    )

    if request.method == "POST":
        location_form = LocationSelectionForm(request.POST, theme=theme)
        photo_form = PhotoForm(request.POST, request.FILES)
        new_location_form = NewLocationForm(request.POST)

        if photo_form.is_valid() and location_form.is_valid():
            photo = photo_form.save(commit=False)
            photo.user = request.user
            photo.theme = theme

            selected_location = location_form.cleaned_data["location"]
            if selected_location:
                photo.location = selected_location

                # Set new location form fields with existing location data
                new_location_form = NewLocationForm(
                    initial={
                        "name": selected_location.name,
                        "latitude": selected_location.latitude,
                        "longitude": selected_location.longitude,
                    }
                )
            elif new_location_form.is_valid():
                new_location = new_location_form.save(commit=False)
                new_location.theme = theme
                if not new_location.name:
                    new_location.name = f"Location at {new_location.latitude:.4f}, {new_location.longitude:.4f}"

                try:
                    new_location.save()
                except IntegrityError:
                    # エラーが発生した場合もフォームを正しく初期化
                    new_location_form.add_error("name", "A location with the same name and theme already exists.")
                    return render(
                        request,
                        "photo/upload.html",
                        {
                            "location_form": location_form,
                            "photo_form": photo_form,
                            "new_location_form": new_location_form,
                            "theme": theme,
                            "locations_json": locations_json,
                            "initial_location": None,
                        },
                    )

                photo.location = new_location
            else:
                messages.error(request, "Please select a location or create a valid new one.")
                return render(
                    request,
                    "photo/upload.html",
                    {
                        "location_form": location_form,
                        "photo_form": photo_form,
                        "new_location_form": new_location_form,
                        "theme": theme,
                        "locations_json": locations_json,
                        "initial_location": None,
                    },
                )

            photo.save()
            messages.success(request, "Photo uploaded successfully.")
            return redirect("theme_detail", theme_id=theme.id)
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        location_form = LocationSelectionForm(theme=theme)
        photo_form = PhotoForm()
        new_location_form = NewLocationForm()

    initial_location = None
    if location_form.initial.get("location"):
        initial_location = Location.objects.filter(id=location_form.initial["location"]).first()
        if initial_location:
            initial_location = {
                "id": initial_location.id,
                "name": initial_location.name,
                "latitude": initial_location.latitude,
                "longitude": initial_location.longitude,
            }

    return render(
        request,
        "photo/upload.html",
        {
            "location_form": location_form,
            "photo_form": photo_form,
            "new_location_form": new_location_form,
            "theme": theme,
            "locations_json": locations_json,
            "initial_location": json.dumps(initial_location) if initial_location else "null",
        },
    )


@login_required
def theme_detail(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id, user=request.user)
    photos = Photo.objects.filter(theme=theme).order_by("-taken_at")
    locations = theme.location_set.prefetch_related(Prefetch("photo_set", queryset=Photo.objects.order_by("-taken_at")))

    return render(
        request,
        "theme/detail.html",
        {
            "theme": theme,
            "photos": photos,
            "locations": locations,
        },
    )


@login_required
def get_locations(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id, user=request.user)
    locations = Location.objects.filter(theme=theme)
    data = [{"id": loc.id, "name": loc.name, "lat": loc.latitude, "lng": loc.longitude} for loc in locations]
    return JsonResponse(data, safe=False)


@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    # 写真の所有者かどうかを確認
    if photo.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this photo.")

    if request.method == "POST":
        theme_id = photo.theme.id
        photo.delete()
        messages.success(request, "Photo deleted successfully.")
        return redirect("theme_detail", theme_id=theme_id)

    return render(request, "photo/confirm_delete.html", {"photo": photo})


@login_required
def view_map(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id, user=request.user)

    # Prefetchを使用して関連する写真を一度に取得し、メモリ効率を向上
    locations = Location.objects.filter(theme=theme).prefetch_related(
        Prefetch("photo_set", queryset=Photo.objects.order_by("-taken_at"))
    )

    locations_data = []
    for location in locations:
        photo_data = [
            {
                "id": photo.id,
                "url": photo.image.url,
                "caption": photo.caption,
                "date": photo.taken_at.strftime("%Y-%m-%d %H:%M") if photo.taken_at else "N/A",
            }
            for photo in location.photo_set.all()  # prefetchされたデータを使用
        ]
        locations_data.append(
            {
                "id": location.id,
                "name": location.name,
                "lat": float(location.latitude),
                "lng": float(location.longitude),
                "photos": photo_data,
            }
        )

    context = {
        "theme": theme,
        "locations_data": json.dumps(locations_data),
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
    }

    # デバッグ情報の追加（開発時のみ使用）
    if settings.DEBUG:
        context.update(
            {
                "debug_locations": locations,
                "debug_photos": Photo.objects.filter(theme=theme),
            }
        )

    return render(request, "map/view.html", context)


@login_required
def edit_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)

    # 地点の所有者かどうかを確認
    if location.theme.user != request.user:
        return HttpResponseForbidden("You don't have permission to edit this location.")

    if request.method == "POST":
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, "Location updated successfully.")
            return redirect("theme_detail", theme_id=location.theme.id)
    else:
        form = LocationForm(instance=location)

    return render(request, "location/edit.html", {"form": form, "location": location})


@login_required
def delete_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)

    # 地点の所有者かどうかを確認
    if location.theme.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this location.")

    if request.method == "POST":
        theme_id = location.theme.id
        # この地点に関連する写真も削除
        Photo.objects.filter(location=location).delete()
        location.delete()
        messages.success(request, "Location and associated photos deleted successfully.")
        return redirect("theme_detail", theme_id=theme_id)

    return render(request, "location/confirm_delete.html", {"location": location})
