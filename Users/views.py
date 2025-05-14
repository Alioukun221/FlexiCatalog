from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from .models import Client, PasswordResetToken

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        telephone = request.POST.get('telephone', '')
       
        
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return render(request, 'inscription.html')
            
        # Vérifier si l'utilisateur existe déjà
        try:
            existing_user = Client.objects(username=username).first()
            if existing_user:
                messages.error(request, "Ce nom d'utilisateur existe déjà")
                return render(request, 'inscription.html')
            
            # Vérifier si l'email existe déjà
            existing_email = Client.objects(email=email).first()
            if existing_email:
                messages.error(request, "Cet email est déjà utilisé")
                return render(request, 'inscription.html')
                
            
            new_client = Client(
                username=username,
                email=email,
                telephone=telephone,
                role='client',
                date_inscription=datetime.utcnow(),
                actif=True
            )
            new_client.set_password(password) 
            new_client.save()
                
            messages.success(request, "Compte créé avec succès. Veuillez vous connecter.")
            return redirect('login')
                
        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")
            return render(request, 'inscription.html')
    
    return render(request, 'inscription.html')

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username') 
        password = request.POST.get('password')
        
        try:
            # Chercher par nom d'utilisateur ou email
            client = Client.objects(username=username_or_email).first()
            if not client:
                client = Client.objects(email=username_or_email).first()
                
            if client and client.check_password(password):
                # Vérifier si le compte est actif
                if not client.actif:
                    messages.error(request, "Votre compte est désactivé. Veuillez contacter l'administrateur.")
                    return render(request, 'connexion.html')
                
                # Créer une session pour l'utilisateur
                request.session['user_id'] = str(client.id)
                request.session['username'] = client.username
                request.session['email'] = client.email
                request.session['role'] = client.role
                
                messages.success(request, f"Bienvenue, {client.username}!")
                return redirect('home') 
            else:
                messages.error(request, "Nom d'utilisateur/email ou mot de passe incorrect")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")
    
    return render(request, 'connexion.html')

def logout_view(request):
    # Supprimer les informations de session
    for key in list(request.session.keys()):
        del request.session[key]
    
    messages.success(request, "Vous avez été déconnecté avec succès")
    return redirect('login')

def home_view(request):
    # Vérifier si l'utilisateur est connecté
    if 'user_id' not in request.session:
        return redirect('login')
    
    return render(request, 'home.html')

def password_reset_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            client = Client.objects(email=email).first()
            
            
            if client:
                # Supprimer les anciens tokens pour cet utilisateur
                PasswordResetToken.objects(client=client).delete()
                
                # Creation d'un nouveau token pour l'utlisateur 
                token = get_random_string(64)
                
                # Temps d'expiration
                expires_at = timezone.now() + timedelta(hours=24)
                
                # Token save dans la base de donnee
                reset_token = PasswordResetToken(
                    client=client,
                    token=token,
                    expires_at=expires_at
                )
                reset_token.save()
                
                # l'url de reinitialisation 
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'token': token})
                )
                
                # Envoyer l'email
                send_mail(
                    'Réinitialisation de votre mot de passe',
                    f'Bonjour {client.username},\n\n'
                    f'Vous avez demandé une réinitialisation de mot de passe. '
                    f'Veuillez cliquer sur le lien suivant pour définir un nouveau mot de passe :\n\n'
                    f'{reset_url}\n\n'
                    f'Ce lien est valable pendant 24 heures.\n\n'
                    f'Si vous n\'avez pas demandé cette réinitialisation, ignorez cet email.\n\n'
                    f'Cordialement,\n'
                    f'L\'équipe de votre application',
                    settings.DEFAULT_FROM_EMAIL,
                    [client.email],
                    fail_silently=False,
                )
            
            messages.success(request, 
                "Si l'adresse e-mail existe dans notre système, vous recevrez "
                "un e-mail avec les instructions pour réinitialiser votre mot de passe."
            )
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")
    
    return render(request, 'password_reset_request.html')

def password_reset_confirm_view(request, token):
    try:
        # Vérifier si le token existe et est valide
        reset_token = PasswordResetToken.objects(
            token=token,
            expires_at__gt=timezone.now(),
            used=False
        ).first()
        
        if not reset_token:
            messages.error(request, "Le lien de réinitialisation est invalide ou a expiré.")
            return redirect('password_reset_request')
        
        # Afficher le formulaire pour définir un nouveau mot de passe
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Vérification de la correspondance des deux mots de passe 
            if new_password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas")
                return render(request, 'password_reset_confirm.html', {'token': token})
            
            # Mise a jour du token 
            client = reset_token.client
            client.set_password(new_password)
            client.save()
            
            # Marquer le token comme utilisé
            reset_token.used = True
            reset_token.save()
            
            messages.success(request, "Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.")
            return redirect('login')
        
        return render(request, 'password_reset_confirm.html', {'token': token})
        
    except Exception as e:
        messages.error(request, f"Une erreur est survenue: {str(e)}")
        return redirect('password_reset_request')

def password_change_view(request):
    """Vue pour changer le mot de passe (pour les utilisateurs connectés)"""
    # Vérifier si l'utilisateur est connecté
    if 'user_id' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Vérifier si les nouveaux mots de passe correspondent
        if new_password != confirm_password:
            messages.error(request, "Les nouveaux mots de passe ne correspondent pas")
            return render(request, 'password_change.html')
        
        try:
            # Récupérer l'utilisateur actuel
            user_id = request.session['user_id']
            client = Client.objects(id=user_id).first()
            
            # Vérifier l'ancien mot de passe
            if not client.check_password(current_password):
                messages.error(request, "Le mot de passe actuel est incorrect")
                return render(request, 'password_change.html')
            
            # Mettre à jour le mot de passe
            client.set_password(new_password)
            client.save()
            
            messages.success(request, "Votre mot de passe a été modifié avec succès")
            return redirect('profile')  # Rediriger vers le profil ou une autre page
            
        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")
    
    return render(request, 'password_change.html')