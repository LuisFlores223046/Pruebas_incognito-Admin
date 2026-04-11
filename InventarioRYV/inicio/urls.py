"""URLs para la página de inicio."""
from django.urls import path
from . import views

app_name = 'inicio'

urlpatterns = [
    path('', views.landing, name='landing'),
]
