from django.shortcuts import render
from produits.models import Produit, Categorie  # Import des modèles MongoDB
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine.errors import NotUniqueError
from .models import NewsletterSubscriber  # le modèle MongoEngine

def page_accueil(request):
    # Récupérer 8 produits phares
    produits_phares = Produit.objects.order_by('-date_creation')[:8]
    
    # Récupérer toutes les catégories
    categories = Categorie.objects.all()
    categories_menu = categories[:5]
    
    # Récupérer des produits spécifiques pour chaque section
    smartphones = Produit.objects.filter(categorie='Smartphones')[:4]
    ordinateurs = Produit.objects.filter(categorie='Ordinateurs')[:4]
    
    return render(request, 'accueil/home.html', {
        'produits_phares': produits_phares,
        'categories': categories,
        'categories_menu': categories_menu,
        'phones': smartphones,
        'featured_products': ordinateurs
    })


@csrf_exempt  # si tu utilises fetch, assure-toi de gérer CSRF correctement (voir plus bas)
def subscribe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            if not email:
                return JsonResponse({'success': False, 'error': 'Email manquant.'})
            
            # Vérifie si l'email existe déjà
            if NewsletterSubscriber.objects(email=email).first():
                return JsonResponse({'success': False, 'error': 'Email déjà inscrit.'})

            # Enregistrer l'email
            subscriber = NewsletterSubscriber(email=email)
            subscriber.save()

            # (Optionnel) envoyer un email ici pour confirmer l'inscription

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'})