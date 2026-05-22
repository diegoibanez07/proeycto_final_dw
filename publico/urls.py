from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio_publico, name='inicio_publico'),
    path('servicios/', views.servicios_publicos, name='servicios_publicos'),
    path('consulta-estado/', views.consulta_estado, name='consulta_estado_publico'),
]
