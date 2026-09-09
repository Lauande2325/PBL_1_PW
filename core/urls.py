from django.urls import path
from . import views

urlpatterns = [
    path('reservas/', views.listar_reservas, name='listar_reservas'),
    path('reservas/criar/', views.criar_reserva, name='criar_reserva'), 
]