from django.urls import path

from .views import download_production_report

urlpatterns = [
    path("download-report/", download_production_report, name="download_report"),
]
