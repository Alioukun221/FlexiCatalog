from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from datetime import datetime, timedelta

from .models import Client, PasswordResetToken
from .forms import (
    ClientRegistrationForm, ClientLoginForm, 
    PasswordResetRequestForm, PasswordResetConfirmForm,
    ClientProfileUpdateForm, ChangePasswordForm
)

import secrets





def register_view(request):
    """Vue pour l'inscription d'un nouveau client"""
    """ if 'client_id' in request.session:
        return redirect('dashboard')   """# Rediriger si déjà connecté
    
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            client = form.save()
            request.session['client_id'] = str(client.id)
            messages.success(request, "Votre compte a été créé avec succès!")
            return redirect('login')
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'Users/inscription.html', {'form': form})


def login_view(request):
    
    if request.method == 'POST':
        form = ClientLoginForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            request.session['client_id'] = str(client.id)
            #messages.success(request, f"Bienvenue, {client.username}!")
            
            # Redirection selon le rôle
            # comment enregistrer un user comme admin ?
            if client.role == 'admin':
                return redirect('dashboard')
            return redirect('dashboard')
    else:
        form = ClientLoginForm()
    
    return render(request, 'Users/connexion.html', {'form': form})


def logout(request):
    """Vue pour la déconnexion"""
    if 'client_id' in request.session:
        del request.session['client_id']
        messages.success(request, "Vous avez été déconnecté avec succès.")
    
    return redirect('login')


def password_reset_request(request):
    """Vue pour demander une réinitialisation de mot de passe"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            reset_token = form.generate_token()
            
            # Préparer l'email de réinitialisation
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', args=[reset_token.token])
            )
            
            email_subject = "Réinitialisation de votre mot de passe"
            email_body = render_to_string('Users/email.html', {
                'user': reset_token.client,
                'reset_url': reset_url,
                'expiry_time': '24 heures'
            })
            
            # Envoyer l'email
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [reset_token.client.email],
                html_message=email_body,
                fail_silently=False
            )
            
            messages.success(
                request, 
                "Un email contenant les instructions de réinitialisation de mot de passe "
                "a été envoyé à votre adresse email."
            )
            return redirect('login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'Users/password_reset.html', {'form': form})



def password_reset_confirm(request, token):
    token_obj = PasswordResetToken.objects(
        token=token,
        used=False,
        expires_at__gt=timezone.now()
    ).first()
    
    if not token_obj:
        messages.error(
            request, 
            "Ce lien de réinitialisation est invalide ou a expiré. "
            "Veuillez faire une nouvelle demande."
        )
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        form = PasswordResetConfirmForm(token, request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request, 
                    "Votre mot de passe a été réinitialisé avec succès. "
                    "Vous pouvez maintenant vous connecter avec votre nouveau mot de passe."
                )
                return redirect('login')
            except Exception as e:
                messages.error(request, "Une erreur s'est produite lors de la réinitialisation.")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordResetConfirmForm(token)
    
    return render(request, 'Users/change_password.html', {'form': form})


def dashboard(request):
    """Vue pour le tableau de bord client"""
    if 'client_id' not in request.session:
        return redirect('login')
    
    client = Client.objects.get(id=request.session['client_id'])
    
    return render(request, 'client/dashboard.html', {'client': client})



def profile(request):
    """Vue pour afficher et modifier le profil utilisateur"""
    if 'client_id' not in request.session:
        return redirect('login')
    
    client = Client.objects.get(id=request.session['client_id'])
    
    if request.method == 'POST':
        form = ClientProfileUpdateForm(client, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès!")
            #return redirect('profile')
    else:
        form = ClientProfileUpdateForm(client)
    
    return render(request, 'Users/profil_user.html', {'form': form, 'client': client})


def change_password(request):
    """Vue pour changer le mot de passe"""
    if 'client_id' not in request.session:
        return redirect('login')
    
    client = Client.objects.get(id=request.session['client_id'])
    
    if request.method == 'POST':
        form = ChangePasswordForm(client, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre mot de passe a été changé avec succès!")
            return redirect('profile')
    else:
        form = ChangePasswordForm(client)
    
    return render(request, 'client/change_password.html', {'form': form})





# Middleware pour vérifier l'authentification
def auth_middleware(get_response):
    def middleware(request):
        # Vérifier si l'utilisateur est connecté
        if 'client_id' in request.session:
            try:
                client = Client.objects.get(id=request.session['client_id'])
                
                # Vérifier si le compte est actif
                if not client.actif:
                    # Déconnecter l'utilisateur si son compte a été désactivé
                    del request.session['client_id']
                    messages.error(
                        request, 
                        "Votre compte a été désactivé. Veuillez contacter l'administrateur."
                    )
                    return redirect('login')
                
            except Client.DoesNotExist:
                # Déconnecter si l'ID du client n'existe pas
                del request.session['client_id']
                return redirect('login')
        
        response = get_response(request)
        return response
    
    return middleware


