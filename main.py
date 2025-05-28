#!/usr/bin/env python3
"""
Script pour créer un admin avec PyMongo direct
"""

import os
import django
from django.contrib.auth.hashers import make_password

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FlexiCatalog.settings')
django.setup()

from Users.models import Client

def create_admin_simple():
    username = input("Username admin: ")
    email = input("Email admin: ")
    password = input("Mot de passe: ")
    
    # Vérification simple
    existing_user = Client.objects.filter(username=username).first()
    if existing_user:
        print(f"❌ L'utilisateur '{username}' existe déjà!")
        return
    
    existing_email = Client.objects.filter(email=email).first()
    if existing_email:
        print(f"❌ L'email '{email}' existe déjà!")
        return
    
    try:
        # Créer l'admin
        admin = Client(
            username=username,
            email=email,
            role='admin',
            password=make_password(password)
        )
        admin.save()
        
        print(f"✅ Admin '{username}' créé avec succès!")
        print(f"ID: {admin.id}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    create_admin_simple()