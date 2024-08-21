import json

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Location, Photo, Theme


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ["name"]


class LocationSelectionForm(forms.Form):
    location = forms.ModelChoiceField(
        queryset=Location.objects.none(), required=False, empty_label="Create new location"
    )

    def __init__(self, *args, **kwargs):
        theme = kwargs.pop("theme", None)
        super(LocationSelectionForm, self).__init__(*args, **kwargs)
        if theme:
            locations = Location.objects.filter(theme=theme)
            self.fields["location"].queryset = locations
            self.fields["location"].widget.attrs["data-coords"] = json.dumps(
                {str(loc.id): {"latitude": loc.latitude, "longitude": loc.longitude} for loc in locations}
            )


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ["image", "caption", "taken_at"]
        widgets = {
            "taken_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class NewLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "latitude", "longitude"]
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "latitude", "longitude"]
