from django.urls import path

from . import views

app_name = "robots"

urlpatterns = [
    path("create/", views.create_robot, name="create_robot"),
]
