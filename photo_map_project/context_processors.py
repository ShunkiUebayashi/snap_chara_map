# my_app/context_processors.py
import os


def global_vars(request):
    google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    return {"google_maps_api_key": google_maps_api_key, "GOOGLE_MAPS_API_KEY": google_maps_api_key}
