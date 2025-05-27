from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .form import CategorieForm, ProduitFormEtape1, ProduitFormEtape2
from produits.models import Produit, CATEGORIES, Categorie
import os
import uuid
import logging
from django.utils.text import slugify

logger = logging.getLogger(__name__)

# Create your views here.

def dashboard(request):
    categories = Categorie.objects.all()
    return render(request, 'admindashboard/dashboard.html', {'categories': categories})



def ajouter_categorie(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Récupération des données
                nom = form.cleaned_data['nom']
                description = form.cleaned_data['description']
                
                # Créer la catégorie
                categorie = Categorie(
                    nom=nom,
                    description=description
                )
                
                # Gérer l'image si elle est fournie
                if 'image' in request.FILES:
                    image = request.FILES['image']
                    # Créer un nom de fichier unique
                    filename = f"{slugify(nom)}-{uuid.uuid4().hex[:8]}{os.path.splitext(image.name)[1]}"
                    image_path = os.path.join('static', 'img', filename)
                    
                    # Créer le répertoire img s'il n'existe pas
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    
                    # Sauvegarder l'image
                    with open(image_path, 'wb+') as destination:
                        for chunk in image.chunks():
                            destination.write(chunk)
                    
                    # Stocker l'URL relative
                    categorie.image_url = f'/static/img/{filename}'
                
                categorie.save()
                messages.success(request, f'Catégorie "{nom}" créée avec succès!')
                return redirect('liste_categories')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création de la catégorie: {str(e)}')
    else:
        form = CategorieForm()
    
    return render(request, 'admindashboard/ajouter_categorie.html', {'form': form})

def modifier_categorie(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    
    if request.method == 'POST':
        try:
            categorie.nom = request.POST.get('nom')
            categorie.description = request.POST.get('description')
            categorie.image_url = request.POST.get('image_url')
            categorie.save()
            messages.success(request, f'Catégorie "{categorie.nom}" modifiée avec succès!')
            return redirect('liste_categories')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification de la catégorie: {str(e)}')
    
    return render(request, 'produits/modifier_categorie.html', {'categorie': categorie})


def supprimer_categorie(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    if request.method == 'POST':
        try:
            nom = categorie.nom
            categorie.delete()
            messages.success(request, f'Catégorie "{nom}" supprimée avec succès!')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression de la catégorie: {str(e)}')
    return redirect('liste_categories')


def ajouter_produit_etape1(request):
    if request.method == 'POST':
        form = ProduitFormEtape1(request.POST, request.FILES)
        logger.info(f"Formulaire soumis avec la catégorie: {request.POST.get('categorie')}")
        
        if form.is_valid():
            try:
                # Sauvegarder les données de base dans la session
                produit_data = {
                    'nom': form.cleaned_data['nom'],
                    'description': form.cleaned_data['description'],
                    'prix': form.cleaned_data['prix'],
                    'stock': form.cleaned_data['stock'],
                    'categorie': form.cleaned_data['categorie'],
                    'marque': form.cleaned_data['marque'],
                }
                
                # Gérer l'image seulement si elle est fournie
                if 'image' in request.FILES:
                    image = request.FILES['image']
                    # Créer un nom de fichier temporaire unique
                    temp_filename = f"temp_{uuid.uuid4().hex[:8]}{os.path.splitext(image.name)[1]}"
                    temp_path = os.path.join('static', 'temp', temp_filename)
                    
                    # Créer le répertoire temp s'il n'existe pas
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                    
                    # Sauvegarder l'image temporairement
                    with open(temp_path, 'wb+') as destination:
                        for chunk in image.chunks():
                            destination.write(chunk)
                    
                    # Stocker le chemin de l'image temporaire dans la session
                    produit_data['temp_image_path'] = temp_path
                
                request.session['produit_data'] = produit_data
                return redirect('ajouter_produit_etape2')
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout du produit: {str(e)}")
                messages.error(request, f'Erreur lors de l\'ajout du produit: {str(e)}')
        else:
            logger.warning(f"Erreurs de validation du formulaire: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ProduitFormEtape1()
    
    return render(request, 'admindashboard/ajouter_produit_etape1.html', {
        'form': form,
        'categories': CATEGORIES
    })

def ajouter_produit_etape2(request):
    # Vérifier si on a les données de l'étape 1
    produit_data = request.session.get('produit_data')
    if not produit_data:
        messages.error(request, 'Veuillez d\'abord remplir les informations de base du produit.')
        return redirect('ajouter_produit_etape1')

    if request.method == 'POST':
        form = ProduitFormEtape2(request.POST, categorie=produit_data['categorie'])
        if form.is_valid():
            try:
                # Créer le produit avec toutes les données
                caracteristiques = {}
                for key, value in form.cleaned_data.items():
                    if key.startswith('caracteristique_'):
                        champ = key.replace('caracteristique_', '')
                        caracteristiques[champ] = value

                produit = Produit(
                    nom=produit_data['nom'],
                    description=produit_data['description'],
                    prix=produit_data['prix'],
                    stock=produit_data['stock'],
                    categorie=produit_data['categorie'],
                    marque=produit_data['marque'],
                    caracteristiques=caracteristiques
                )

                # Gérer l'image si elle existe
                if 'temp_image_path' in produit_data:
                    temp_path = produit_data['temp_image_path']
                    if os.path.exists(temp_path):
                        # Créer le nom de fichier final
                        filename = f"{produit.nom}-{uuid.uuid4().hex[:8]}{os.path.splitext(temp_path)[1]}"
                        final_path = os.path.join('static', 'img', filename)
                        
                        # Créer le répertoire img s'il n'existe pas
                        os.makedirs(os.path.dirname(final_path), exist_ok=True)
                        
                        # Déplacer l'image temporaire vers son emplacement final
                        os.rename(temp_path, final_path)
                        produit.image_url = f'/static/img/{filename}'

                produit.save()
                # Nettoyer la session
                del request.session['produit_data']
                messages.success(request, 'Produit ajouté avec succès!')
                return redirect('liste_produits')
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout du produit: {str(e)}")
                messages.error(request, f'Erreur lors de l\'ajout du produit: {str(e)}')
    else:
        form = ProduitFormEtape2(categorie=produit_data['categorie'])
    
    return render(request, 'admindashboard/ajouter_produit_etape2.html', {
        'form': form,
        'produit_data': produit_data
    })

def modifier_produit(request, slug):
    produit = Produit.objects.get(slug=slug)
    if request.method == 'POST':
        form = ProduitFormEtape1(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Mettre à jour le produit existant
                data = form.cleaned_data
                produit.nom = data['nom']
                produit.description = data['description']
                produit.prix = data['prix']
                produit.stock = data['stock']
                produit.categorie = data['categorie']
                produit.marque = data['marque']
                
                # Gérer l'image si une nouvelle est fournie
                if 'image' in request.FILES:
                    image = request.FILES['image']
                    filename = f"{produit.nom}-{uuid.uuid4().hex[:8]}{os.path.splitext(image.name)[1]}"
                    image_path = os.path.join('static', 'img', filename)
                    with open(image_path, 'wb+') as destination:
                        for chunk in image.chunks():
                            destination.write(chunk)
                    produit.image_url = f'/static/img/{filename}'
                
                produit.save()
                messages.success(request, 'Produit modifié avec succès!')
                return redirect('liste_produits')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification du produit: {str(e)}')
    else:
        # Pré-remplir le formulaire avec les données existantes
        initial_data = {
            'nom': produit.nom,
            'description': produit.description,
            'prix': produit.prix,
            'stock': produit.stock,
            'categorie': produit.categorie,
            'marque': produit.marque
        }
        form = ProduitFormEtape1(initial=initial_data)
    
    return render(request, 'admindashboard/ajouter_produit_etape1.html', {
        'form': form,
        'produit': produit,
        'categories': CATEGORIES,
        'is_edit': True
    })

def supprimer_produit(request, slug):
    try:
        produit = Produit.objects.get(slug=slug)
        if request.method == 'POST':
            try:
                # Supprimer l'image
                if produit.image_url:
                    image_path = os.path.join('static', 'img', os.path.basename(produit.image_url))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                
                produit.delete()
                messages.success(request, 'Produit supprimé avec succès!')
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression du produit: {str(e)}')
    except Produit.DoesNotExist:
        messages.error(request, 'Le produit demandé n\'existe pas.')
    
    return redirect('liste_produits')

def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'admindashboard/liste_produits.html', {
        'produits': produits
    })







