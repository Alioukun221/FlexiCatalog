from django.urls import path
from . import views
from .views import subscribe


urlpatterns = [
    path('', views.page_accueil, name='accueil'),
]