from django.urls import path

from .views import (
    log_viewer_page,
    get_log_files,
    get_log_content,
    delete_log_file,
    clear_log_file,
)

app_name = "log_viewer"

urlpatterns = [
    path("", log_viewer_page, name="log_viewer"),
    path("api/files", get_log_files, name="log_viewer_files"),
    path("api/content", get_log_content, name="log_viewer_content"),
    path("api/file", delete_log_file, name="log_viewer_delete"),
    path("api/clear", clear_log_file, name="log_viewer_clear"),
]
