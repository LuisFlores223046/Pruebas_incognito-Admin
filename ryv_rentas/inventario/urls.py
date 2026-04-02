"""URLs para el módulo de inventario."""
from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.lista_inventario, name='lista'),
    path('<int:pk>/', views.detalle_equipo, name='detalle'),
    path('nuevo/', views.crear_equipo, name='crear'),
    path('<int:pk>/editar/', views.editar_equipo, name='editar'),
    path('<int:pk>/baja/', views.dar_baja_equipo, name='baja'),
    path('solicitar/', views.solicitar_cambio, name='solicitar'),
]
