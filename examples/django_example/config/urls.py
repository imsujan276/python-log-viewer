from django.urls import path, include

urlpatterns = [
    path("logs/", include("python_log_viewer.contrib.django.urls")),
]
