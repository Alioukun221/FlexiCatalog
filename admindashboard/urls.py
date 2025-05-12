from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ajouter-categorie/', views.ajouter_categorie, name='ajouter_categorie'),
    path('ajouter-produit/', views.ajouter_produit_etape1, name='ajouter_produit_etape1'),
    path('ajouter-produit/etape2/', views.ajouter_produit_etape2, name='ajouter_produit_etape2'),
    path('modifier-produit/<str:produit_id>/', views.modifier_produit, name='modifier_produit'),
    path('supprimer-produit/<str:produit_id>/', views.supprimer_produit, name='supprimer_produit'),
    path('liste-produits/', views.liste_produits, name='liste_produits'),
] 