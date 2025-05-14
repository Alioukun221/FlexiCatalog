from django.db import models
import Users.mongo_config
from mongoengine import *
import datetime
from django.utils import timezone

# Create your models here.

ROLES = ('client', 'admin')



class Client(Document):
    username = StringField(max_length=100, required=True, unique=True)
    password_hash = StringField(required=True)
    email = EmailField(required=True, unique=True)
    telephone = StringField(regex=r'^((\+221)|(00221))?[2-9][0-9]{8}$')
    role = StringField(choices=ROLES, default='client')
    date_inscription = DateTimeField(default=datetime.utcnow)
    actif = BooleanField(default=True)

    meta = {
        'collection': 'Users',
        'indexes': [
            'username',
            'email'
        ]
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
    
   