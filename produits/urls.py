from django.urls import path
from . import views
from .views import rechercher_produits_api

app_name = 'products'

urlpatterns = [
    path('search/', views.search_products, name='search_products'),
    path('produits/', views.afficher_produits, name='liste_produits'),   
    path('categories/', views.liste_categories, name='liste_categories'),
    path('produit/<slug:slug>/', views.afficher_produit_spécifique, name='produit_spécifique'),
    path('categorie/<slug:slug>/', views.detail_categorie, name='detail_categorie'),
    path('api/recherche/', rechercher_produits_api, name='recherche_produits_api'),
] 