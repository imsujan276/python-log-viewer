from django.apps import AppConfig


class LogViewerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "python_log_viewer.contrib.django"
    label = "python_log_viewer"
    verbose_name = "Log Viewer"
