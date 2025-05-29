from django.db import models
from mongoengine import *
#from mongoengine import TextField 
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from produits.models import Produit

# Create your models here.

ROLES = ('client', 'admin')


class Client(Document):
    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True, unique=True)
    telephone = StringField(default = '+221783453456')
    adresse = StringField(default = 'Cite keur Gorgui')
    ville = StringField(default = 'Dakar')
    code_postal = StringField(default ='20054 Dakar/Sénégal')
    pays = StringField(default= 'Senegal')
    password = StringField(required=True)  # Stockera le mot de passe hashé
    role = StringField(default='client')
    date_inscription = DateTimeField()
    actif = BooleanField(default=True)

    # Required for Django authentication compatibility
    @property
    def is_authenticated(self):
        return True # Or add logic to check if the user is genuinely authenticated

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.actif # Use the 'actif' field to determine if the user is active

    def get_id(self):
        return str(self.id) # Return the MongoDB ObjectId as a string
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    meta = {
        'collection':'Users'
    }

class PasswordResetToken(EmbeddedDocument):
    client = ReferenceField(Client, required=True)
    token = StringField(required=True)
    created_at = DateTimeField(default=timezone.now)
    expires_at = DateTimeField(required=True)
    used = BooleanField(default=False)
    
    meta = {
        'collection': 'password_reset_tokens',
        'indexes': [
            'token',
            'expires_at'
        ]
    }

class Commentaire(Document):
    user = ReferenceField(Client, required=True)
    produit = ReferenceField(Produit, required=True)
    contenu = StringField(required=True)
    note = IntField(min_value=1, max_value=5)
    date_creation = DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'commentaires',
        'ordering': ['-date_creation']  # c'est pour afficher les commentaires les plus recents en premier 
    }



    

    
   