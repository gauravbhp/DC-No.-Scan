from django.urls import path, include
from app import views

urlpatterns = [
    path('', views.scanner, name='scanner'),  # Root URL points to scanner
    path('internal-gate-out/', views.internal_gate_out, name='internal_gate_out'),
    path('commercial-plant-gate-out/', views.commercial_plant_gate_out, name='commercial_plant_gate_out'),
    path("__reload__/", include("django_browser_reload.urls")),  # For browser reload
]
