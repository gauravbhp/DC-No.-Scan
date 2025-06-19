from django.urls import path, include
from .views import scanner, gate_out

urlpatterns = [
    path('', scanner, name='scanner'),
    path('gate-out/', gate_out, name='gate_out'),
    path("__reload__/", include("django_browser_reload.urls")),
]