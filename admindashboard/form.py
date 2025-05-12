from django import forms
from produits.models import Produit, CATEGORIES
import os
import uuid
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)


class ProduitFormEtape1(forms.Form):
    nom = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'})
    )
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description du produit', 'rows': 3})
    )
    prix = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix', 'step': '0.01'})
    )
    stock = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité en stock'})
    )
    categorie = forms.ChoiceField(
        choices=[(cat, cat) for cat in CATEGORIES.keys()],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    marque = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marque du produit'})
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

class ProduitFormEtape2(forms.Form):
    def __init__(self, *args, **kwargs):
        self.categorie = kwargs.pop('categorie', None)
        super().__init__(*args, **kwargs)
        
        if self.categorie and self.categorie in CATEGORIES:
            logger.info(f"Ajout des champs dynamiques pour la catégorie: {self.categorie}")
            for champ, field in CATEGORIES[self.categorie].items():
                self.fields[f'caracteristique_{champ}'] = forms.CharField(
                    required=field.required,
                    label=champ.replace('_', ' ').title(),
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': f'Entrez {champ.replace("_", " ").title()}'
                    })
                )
                logger.debug(f"Champ ajouté: caracteristique_{champ} (requis: {field.required})")

    def clean(self):
        cleaned_data = super().clean()
        if self.categorie and self.categorie in CATEGORIES:
            for champ, field in CATEGORIES[self.categorie].items():
                field_name = f'caracteristique_{champ}'
                if field.required and not cleaned_data.get(field_name):
                    self.add_error(field_name, f'Ce champ est requis pour la catégorie {self.categorie}')
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        caracteristiques = {}
        
        # Extraire les caractéristiques dynamiques
        for key, value in data.items():
            if key.startswith('caracteristique_'):
                champ = key.replace('caracteristique_', '')
                caracteristiques[champ] = value

        # Gérer l'image
        image_url = ''
        if 'image' in data and data['image']:
            image = data['image']
            # Générer un nom de fichier unique
            filename = f"{slugify(data['nom'])}-{uuid.uuid4().hex[:8]}{os.path.splitext(image.name)[1]}"
            # Chemin complet pour sauvegarder l'image
            image_path = os.path.join('static', 'img', filename)
            # Sauvegarder l'image
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            # Stocker l'URL relative
            image_url = f'/static/img/{filename}'

        produit = Produit(
            nom=data['nom'],
            description=data['description'],
            prix=data['prix'],
            stock=data['stock'],
            categorie=self.categorie,
            marque=data['marque'],
            image_url=image_url,
            caracteristiques=caracteristiques
        )
        produit.save()
        return produit



class CategorieForm(forms.Form):
    nom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'})
    )
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description de la catégorie', 'rows': 3})
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

