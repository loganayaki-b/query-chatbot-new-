from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("messages/create/", views.create_message, name="create_message"),
]
