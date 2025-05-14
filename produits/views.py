from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Produit, Categorie, CATEGORIES
from datetime import datetime


def afficher_produits(request):
    produits = Produit.objects.all()
    return render(request, 'produits/produits.html', {'produits': produits})


def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'produits/liste_categories.html', {'categories': categories})

def detail_categorie(request, slug):
    categorie = Categorie.objects.get(slug=slug)
    produits = Produit.objects.filter(categorie=categorie.nom)
    return render(request, 'produits/detail_categorie.html', {'categorie': categorie, 'produits': produits})
    

def afficher_produit_spécifique(request, slug):
    produit = Produit.objects.get(slug=slug)
    # Récupérer tous les produits de la même catégorie, exclure le produit actuel et limiter à 4
    produits_similaires = [p for p in Produit.objects.all() 
                          if p.categorie == produit.categorie and p.slug != produit.slug][:4]
    return render(request, 'produits/produit_spécifique.html', {'produit': produit, 'produits_similaires': produits_similaires})







