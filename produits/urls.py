from django.urls import path
from . import views

urlpatterns = [
    path('', views.afficher_produits, name='produits'),
    path('produits/', views.afficher_produits, name='liste_produits'),   
    path('categories/', views.liste_categories, name='liste_categories'),
] 