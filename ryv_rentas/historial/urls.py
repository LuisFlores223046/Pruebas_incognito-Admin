"""URLs para el módulo de historial."""
from django.urls import path
from . import views

app_name = 'historial'

urlpatterns = [
    path('', views.historial_lista, name='lista'),
    path('<int:pk>/', views.historial_detalle, name='detalle'),
]
