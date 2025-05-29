from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Produit, Client, Commentaire
from .commentaireForm import CommentaireForm

def detail_produit(request, produit_id):
    """Affichage d'un produit et du formulaire pour commentaire"""
    try:
        produit = Produit.objects.get(id=produit_id)
    except Produit.DoesNotExist:
        messages.error(request, "Produit non trouvé")
        return redirect('liste_produits')
    
    # Récupérer tous les commentaires du produit
    commentaires = Commentaire.objects.filter(produit=produit)
    
    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            # Créer ou récupérer l'utilisateur
            user, created = Client.objects.get_or_create(
                email=form.cleaned_data['user_email'],
                defaults={'nom': form.cleaned_data['user_nom']}
            )
            
            # Créer le commentaire
            commentaire = Commentaire(
                user=user,
                produit=produit,
                contenu=form.cleaned_data['contenu'],
                note=form.cleaned_data['note']
            )
            commentaire.save()
            
            messages.success(request, "Commentaire ajouté avec succès !")
            return redirect('detail_produit', produit_id=produit_id)
    else:
        form = CommentaireForm()
    
    context = {
        'produit': produit,
        'commentaires': commentaires,
        'form': form,
        'nb_commentaires': commentaires.count()
    }
    
    return render(request, 'produits/detail.html', context)

def tous_commentaires_produit(request, produit_id):
    """Affiche tous les commentaires d'un produit"""
    produit = get_object_or_404(Produit, id=produit_id)
    commentaires = Commentaire.objects.filter(produit=produit)
    
    return render(request, 'commentaires/liste.html', {
        'produit': produit,
        'commentaires': commentaires
    })