"""URLs raíz del proyecto RYV Rentas."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('inicio.urls')),
    path('auth/', include('authentication.urls')),
    path('inventario/', include('inventario.urls')),
    path('rentas/', include('rentas.urls')),
    path('historial/', include('historial.urls')),
    path('reportes/', include('reportes.urls')),
    path('admin-panel/', include('panel_admin.urls')),
    path('solicitudes/', include('solicitudes.urls')),
]

handler403 = 'config.views.error_403'
handler404 = 'config.views.error_404'
handler500 = 'config.views.error_500'
