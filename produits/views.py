from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Produit, Categorie
from datetime import datetime


def afficher_produits(request):
    produits = Produit.objects.all()
    return render(request, 'produits.html', {'produits': produits})


def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'liste_categories.html', {'categories': categories})







