from django.urls import path
from . import views

urlpatterns = [
    path('', views.afficher_produits, name='produits'),
    path('produits/', views.afficher_produits, name='liste_produits'),   
    path('categories/', views.liste_categories, name='liste_categories'),
    path('produit/<slug:slug>/', views.afficher_produit_spécifique, name='produit_spécifique'),
    path('categorie/<slug:slug>/', views.detail_categorie, name='detail_categorie'),
] 