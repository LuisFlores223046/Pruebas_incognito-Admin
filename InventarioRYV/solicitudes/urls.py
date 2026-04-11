"""URLs para el módulo de solicitudes."""
from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    path(
        'mis-solicitudes/',
        views.mis_solicitudes,
        name='mis_solicitudes',
    ),
]
