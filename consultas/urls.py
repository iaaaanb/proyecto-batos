from django.urls import path
from . import views

app_name = "consultas"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("distribucion-rama/", views.distribucion_rama, name="distribucion_rama"),
    path("indicadores/", views.indicadores, name="indicadores"),
    path("brecha/", views.brecha, name="brecha"),
]
