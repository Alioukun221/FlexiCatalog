from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_GET
from .models import Produit, Categorie, CATEGORIES
from datetime import datetime
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
from mongoengine.queryset.visitor import Q
import logging

logger = logging.getLogger('admindashboard')

def afficher_produits(request):
    produits_list = Produit.objects.all()
    paginator = Paginator(produits_list, 12)  
    page = request.GET.get('page')
    produits = paginator.get_page(page)
    return render(request, 'produits/produits.html', {'produits': produits})


def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'produits/liste_categories.html', {'categories': categories})

def detail_categorie(request, slug):
    categorie = Categorie.objects.get(slug=slug)
    produits = Produit.objects.filter(categorie__icontains=categorie.nom)
    return render(request, 'produits/detail_categorie.html', {'categorie': categorie, 'produits': produits})


def afficher_produit_spécifique(request, slug):
    produit = Produit.objects.get(slug=slug)
    # Récupérer tous les produits de la même catégorie, exclure le produit actuel et limiter à 4
    produits_similaires = [p for p in Produit.objects.all() 
                          if p.categorie == produit.categorie and p.slug != produit.slug][:4]
    return render(request, 'produits/produit_spécifique.html', {'produit': produit, 'produits_similaires': produits_similaires})


@require_GET
def search_products(request):
    query = request.GET.get('q', '').strip()
    if query:

        produits = Produit.objects.filter(
            Q(nom__icontains=query) | Q(description__icontains=query)
        )
        
        # Handle sorting
        sort = request.GET.get('sort', 'relevance')
        if sort == 'price_asc':
            produits = produits.order_by('prix')
        elif sort == 'price_desc':
            produits = produits.order_by('-prix')
        elif sort == 'name_asc':
            produits = produits.order_by('nom')
        elif sort == 'name_desc':
            produits = produits.order_by('-nom')
        
        return render(request, 'produits/search_results.html', {
            'produits': produits,
            'query': query
        })
    return render(request, 'produits/search_results.html', {
        'produits': [],
        'query': ''
    })




def rechercher_produits_api(request):
    query = request.GET.get('q', '')
    if query:
        produits = Produit.objects.filter(nom__icontains=query)[:6]
        resultats = []
        for produit in produits:
            resultats.append({
                'nom': produit.nom,
                'slug': produit.slug,
                'image_url': produit.image_url if produit.image_url else '',
                'prix': float(produit.prix),
            })
        return JsonResponse(resultats, safe=False)
    return JsonResponse([], safe=False)
    
def liste_produits(request):
    params = request.GET
    
    produits = Produit.objects.filter(is_active=True)
    
    q = params.get('q')
    if q:
        produits = produits.filter(nom__icontains=q)
    
    categorie = params.get('categorie')
    if categorie:
        produits = produits.filter(categorie=categorie)
    
    marque = params.get('marque')
    if marque:
        produits = produits.filter(marque__icontains=marque)
    
    prix_min = params.get('prix_min')
    if prix_min:
        produits = produits.filter(prix__gte=prix_min)
    
    prix_max = params.get('prix_max')
    if prix_max:
        produits = produits.filter(prix__lte=prix_max)
    
    # Filtre dynamique selon catégorie
    if categorie == 'Smartphones':
        ram = params.get('ram')
        if ram:
            produits = produits.filter(caracteristiques__ram__icontains=ram)
    
    # Préparer la liste des catégories (extraites de ta constante CATEGORIES)
    categories = list(CATEGORIES.keys())
    
    context = {
        'produits': produits,
        'params': params,
        'categories': categories,
    }
    return render(request, 'produits/liste.html', context)

def search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    marque = request.GET.get('marque', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    ram = request.GET.get('ram', '')
    storage = request.GET.get('storage', '')
    camera = request.GET.get('camera', '')
    battery = request.GET.get('battery', '')
    sort_by = request.GET.get('sort_by', '')
    
    # Initialiser la requête de base
    produits = Produit.objects.all()
    
    # Recherche simple
    if query:
        produits = produits.filter(
            Q(nom__icontains=query) |
            Q(description__icontains=query) |
            Q(marque__icontains=query)
        )
    
    # Filtres avancés
    if category:
        try:
            
            produits = produits.filter(categorie__id=category)
        except:
            pass
    
    if marque:
        produits = produits.filter(marque__icontains=marque)
    
    if min_price:
        try:
            produits = produits.filter(prix__gte=float(min_price))
        except:
            pass
    
    if max_price:
        try:
            produits = produits.filter(prix__lte=float(max_price))
        except:
            pass
    
    # Filtres sur les caractéristiques
    if ram:
        produits = produits.filter(caracteristiques__ram=ram)
    
    if storage:
        produits = produits.filter(caracteristiques__stockage=storage)
    
    if camera:
        produits = produits.filter(caracteristiques__camera=camera)
    
    if battery:
        produits = produits.filter(caracteristiques__batterie=battery)
    
    # Tri
    if sort_by:
        if sort_by == 'price_asc':
            produits = produits.order_by('prix')
        elif sort_by == 'price_desc':
            produits = produits.order_by('-prix')
        elif sort_by == 'name_asc':
            produits = produits.order_by('nom')
        elif sort_by == 'name_desc':
            produits = produits.order_by('-nom')
    
    # Pagination
    paginator = Paginator(produits, 12)  
    page = request.GET.get('page', 1)
    try:
        produits = paginator.get_page(page)
    except:
        produits = paginator.get_page(1)
    
    # Récupérer toutes les catégories pour le filtre
    categories = Categorie.objects.all()
    
    context = {
        'produits': produits,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'marque': marque,
        'min_price': min_price,
        'max_price': max_price,
        'ram': ram,
        'storage': storage,
        'camera': camera,
        'battery': battery,
        'sort_by': sort_by,
    }
    
    return render(request, 'produits/search.html', context)



