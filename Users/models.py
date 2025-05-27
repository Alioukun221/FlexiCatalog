from django.db import models
from mongoengine import *
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

ROLES = ('client', 'admin')



class Client(Document):
    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)  # Stockera le mot de passe hashé
    role = StringField(default='client')
    date_inscription = DateTimeField()
    actif = BooleanField(default=True)
    
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    meta = {
        'collection':'Users'
    }



class PasswordResetToken(Document):
    client = ReferenceField(Client, required=True)
    token = StringField(required=True)
    created_at = DateTimeField(default=timezone.now)
    expires_at = DateTimeField(required=True)
    used = BooleanField(default=False)
    
    meta = {
        'collection': 'password_reset_tokens',
        'indexes': [
            'client',
            'token',
            'expires_at'
        ]
    }
    
   