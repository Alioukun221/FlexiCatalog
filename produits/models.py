from mongoengine import (
    Document, StringField, FloatField, IntField, DateTimeField,
    ListField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField, ImageField, DictField, DynamicField, BooleanField
)
from datetime import datetime
import os
from mongoengine.errors import ValidationError
from slugify import slugify
import uuid
from django.db import models


# Définition des catégories et leurs champs spécifiques
CATEGORIES = {
    'Smartphones': {
        'ecran': StringField(required=True),
        'processeur': StringField(required=True),
        'ram': StringField(required=True),
        'stockage': StringField(required=True),
        'couleur': StringField(required=True),
        'appareil_photo': StringField(),
        'batterie': StringField(),
        'systeme': StringField(),
        'connectivite': StringField(),
        'resistance_eau': StringField(),
        'charge_rapide': StringField(),
        'biometrie': StringField()
    },
    'Ordinateurs': {
        'ecran': StringField(required=True),
        'processeur': StringField(required=True),
        'ram': StringField(required=True),
        'stockage': StringField(required=True),
        'carte_graphique': StringField(),
        'systeme': StringField(),
        'connectivite': StringField(),
        'type_ordinateur': StringField(required=True),
        'poids': StringField(),
        'autonomie': StringField(),
        'ports': StringField(),
        'clavier': StringField()
    },
    'Audio': {
        'type': StringField(required=True),
        'connectivite': StringField(required=True),
        'autonomie': StringField(required=True),
        'reduction_bruit': StringField(),
        'couleur': StringField(),
        'puissance': StringField(),
        'impedance': StringField(),
        'frequence': StringField(),
        'microphone': StringField(),
        'resistance_eau': StringField(),
        'bluetooth_version': StringField()
    },
    'Wearables': {
        'ecran': StringField(required=True),
        'autonomie': StringField(required=True),
        'resistance': StringField(required=True),
        'systeme': StringField(),
        'capteurs': ListField(StringField()),
        'type_appareil': StringField(required=True),
        'connectivite': StringField(),
        'compatibilite': StringField(),
        'fonctions_sport': StringField(),
        'resistance_eau': StringField(),
        'charge_rapide': StringField()
    },
    'Photo': {
        'capteur': StringField(required=True),
        'video': StringField(required=True),
        'stabilisation': StringField(),
        'connectivite': StringField(),
        'objectifs': ListField(StringField()),
        'type_appareil': StringField(required=True),
        'resolution': StringField(required=True),
        'zoom': StringField(),
        'mode_nuit': StringField(),
        'resistance_eau': StringField(),
        'format_photo': StringField()
    },
    'Tablettes': {
        'ecran': StringField(required=True),
        'processeur': StringField(required=True),
        'ram': StringField(required=True),
        'stockage': StringField(required=True),
        'systeme': StringField(required=True),
        'connectivite': StringField(),
        'autonomie': StringField(),
        'camera': StringField(),
        'stylo': StringField(),
        'resistance_eau': StringField(),
        'charge_rapide': StringField()
    },
    'Gaming': {
        'type_appareil': StringField(required=True),
        'processeur': StringField(required=True),
        'carte_graphique': StringField(required=True),
        'ram': StringField(required=True),
        'stockage': StringField(required=True),
        'ecran': StringField(),
        'clavier': StringField(),
        'souris': StringField(),
        'connectivite': StringField(),
        'rgb': StringField(),
        'compatibilite': StringField()
    },
    'Accessoires': {
        'type_accessoire': StringField(required=True),
        'compatibilite': StringField(required=True),
        'connectivite': StringField(),
        'couleur': StringField(),
        'materiaux': StringField(),
        'dimensions': StringField(),
        'poids': StringField(),
        'resistance': StringField(),
        'garantie': StringField(),
        'caracteristiques_speciales': StringField()
    },
    'Reseaux': {
        'type_appareil': StringField(required=True),
        'debit': StringField(required=True),
        'portee': StringField(required=True),
        'frequence': StringField(),
        'ports': StringField(),
        'securite': StringField(),
        'nombre_antennes': StringField(),
        'compatibilite': StringField(),
        'poe': StringField(),
        'vpn': StringField()
    },
    'Stockage': {
        'type_stockage': StringField(required=True),
        'capacite': StringField(required=True),
        'interface': StringField(required=True),
        'vitesse_lecture': StringField(),
        'vitesse_ecriture': StringField(),
        'format': StringField(),
        'compatibilite': StringField(),
        'garantie': StringField(),
        'resistance': StringField(),
        'encryption': StringField()
    }
}

class Categorie(Document):
    nom = StringField(required=True, max_length=100)
    description = StringField(required=True)
    slug = StringField(unique=True)
    image_url = StringField() 

    meta = {
        'collection': 'categories',
        'indexes': ['nom'],
        'ordering': ['nom']
    }

    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        # Génération automatique du slug si non défini
        if not self.slug:
            unique_id = str(uuid.uuid4())[:8]  # Génère un identifiant unique
            self.slug = slugify(self.nom) + '-' + unique_id
        super().save(*args, **kwargs)

    def get_image_path(self):
        if self.image_url:
            return f'/static/img/{os.path.basename(self.image_url)}'
        return None


    
# Modèle Produit avec champs dynamiques
class Produit(Document):
    nom = StringField(required=True, max_length=200)
    description = StringField(required=True)
    slug = StringField(unique=True)
    prix = FloatField(required=True)
    stock = IntField(required=True, default=0)
    image_url = StringField() 
    categorie = StringField(required=True, choices=list(CATEGORIES.keys()))
    marque = StringField(required=True, max_length=100)
    date_creation = DateTimeField(default=datetime.utcnow)
    date_modification = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=True)
    caracteristiques = DictField()
    image = models.ImageField(upload_to='produits_images/', blank=True, null=True)

    meta = {
        'collection': 'produits',
        'indexes': ['nom', 'categorie', 'marque'],
        'ordering': ['-nom']
    }

    def __str__(self):
        return self.nom

    def get_image_path(self):
        if self.image_url:
            return f'/static/img/{os.path.basename(self.image_url)}'
        return None

    def get_champs_requis(self):
        return CATEGORIES.get(self.categorie, {})

    def get_champs_disponibles(self):
        return CATEGORIES.get(self.categorie, {})

    def clean(self):
        super().clean()
        champs_requis = self.get_champs_requis()
        for champ, field in champs_requis.items():
            if field.required and champ not in self.caracteristiques:
                raise ValidationError(f"Le champ {champ} est requis pour la catégorie {self.categorie}")

    def save(self, *args, **kwargs):
        # Génération automatique du slug si non défini
        if not self.slug:
            unique_id = str(uuid.uuid4())[:8]  # Génère un identifiant unique
            self.slug = slugify(self.nom) + '-' + unique_id
        super().save(*args, **kwargs)


class Order(Document):
    numero_commande = StringField(required=True, unique=True)
    date_commande = DateTimeField(default=datetime.utcnow)
    client = StringField(required=True)
    email = StringField(required=True)
    telephone = StringField(required=True)
    adresse = StringField(required=True)
    produits = ListField(DictField())
    total = FloatField(required=True)
    statut = StringField(required=True, choices=['en_attente', 'confirmee', 'expediee', 'livree', 'annulee'])
    
    meta = {
        'collection': 'commandes',
        'indexes': ['numero_commande', 'date_commande', 'client'],
        'ordering': ['-date_commande']
    }
    
    def __str__(self):
        return f"Commande {self.numero_commande} - {self.client}"
    
    def save(self, *args, **kwargs):
        if not self.numero_commande:
            date_str = datetime.utcnow().strftime('%Y%m%d')
            random_str = str(uuid.uuid4())[:8]
            self.numero_commande = f"CMD-{date_str}-{random_str}"
        super().save(*args, **kwargs)


