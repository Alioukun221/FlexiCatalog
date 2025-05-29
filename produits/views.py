from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Produit, Categorie, CATEGORIES
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .utils import construire_filtre_recherche_v2
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import recherche_filtrée
from django.core.paginator import Paginator
from mongoengine.queryset.visitor import Q


def afficher_produits(request):
    produits = Produit.objects.all()
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
        produits = Produit.objects.filter(nom__icontains=query)[:5]
        results = [{
            'nom': produit.nom,
            'slug': produit.slug,
            'image_url': '/static/img/no_image.png'
        } for produit in produits]
    else:
        results = []
    return JsonResponse(results, safe=False)


# @csrf_exempt
# def rechercher_produits_api(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)

#         filtre = construire_filtre_recherche_v2(data)
#         produits = Produit.objects(__raw__=filtre, is_active=True)

#         resultats = []
#         for p in produits:
#             resultats.append({
#                 'nom': p.nom,
#                 'categorie': p.categorie,
#                 'prix': p.prix,
#                 'marque': p.marque,
#                 'caracteristiques': p.caracteristiques,
#             })

#         return JsonResponse({'produits': resultats})
#     else:
#         return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def rechercher_produits_api(request):
    query = request.GET.get('q', '')
    if query:
        produits = Produit.objects.filter(nom__icontains=query)[:6]
        resultats = []
        for produit in produits:
            resultats.append({
                'nom': produit.nom,
                'slug': produit.slug,
                'image_url': produit.image.url if produit.image else '',
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
    
    # Filtre dynamique selon catégorie (exemple RAM pour Smartphones)
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



