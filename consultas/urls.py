from django.urls import path
from . import views

app_name = "consultas"

urlpatterns = [
    path("personas-por-region/", views.personas_por_region, name="personas_por_region"),
    path("ingreso-por-rama/", views.ingreso_por_rama, name="ingreso_por_rama"),
    path("brecha-salarial/", views.brecha_salarial, name="brecha_salarial"),
]
