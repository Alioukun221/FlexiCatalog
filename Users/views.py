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
# Import cart models and helper function
from cart.models import Cart, CartItem
from cart.views import get_or_create_cart # Assuming this can be imported and used here

import secrets
# Import AnonymousUser
from django.contrib.auth.models import AnonymousUser





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
            # Redirect to a page after successful login, e.g., 'dashboard' or 'accueil'
            return redirect('accueil') 
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'Users/inscription.html', {'form': form})


def login_view(request):
    
    if request.method == 'POST':
        form = ClientLoginForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            
            # --- Cart Migration Logic ---
            # Get the anonymous cart using the session key *before* logging in the user
            anonymous_cart = Cart.objects(session_key=request.session.session_key).first()
            
            # Log in the user by setting the session ID
            request.session['client_id'] = str(client.id)

            # Get or create the authenticated user's cart
            # The get_or_create_cart function should now associate the cart with the logged-in user
            # because request.user will be authenticated after setting client_id (via middleware)
            user_cart = get_or_create_cart(request)

            # Migrate items from the anonymous cart to the user's cart
            if anonymous_cart:
                anonymous_items = CartItem.objects(cart=anonymous_cart)
                for anonymous_item in anonymous_items:
                    # Check if the product is already in the user's cart
                    user_cart_item = CartItem.objects(cart=user_cart, product=anonymous_item.product).first()
                    
                    if user_cart_item:
                        # Product exists, update quantity
                        user_cart_item.quantity += anonymous_item.quantity
                        # Ensure quantity doesn't exceed stock (optional, depends on desired behavior)
                        # if user_cart_item.quantity > user_cart_item.product.stock:
                        #     user_cart_item.quantity = user_cart_item.product.stock
                        user_cart_item.save()
                    else:
                        # Product does not exist, move the item to the user's cart
                        anonymous_item.cart = user_cart
                        anonymous_item.save()
                
                # Delete the anonymous cart after migration
                anonymous_cart.delete()
            # --- End Cart Migration Logic ---

            messages.success(request, "Connexion réussie!")
            # Redirection selon le rôle
            if client.role == 'admin':
                return redirect('dashboard')
            return redirect('accueil')
    else:
        form = ClientLoginForm()
    
    return render(request, 'Users/connexion.html', {'form': form})


def logout(request):
    """Vue pour la déconnexion"""
    if 'client_id' in request.session:
        del request.session['client_id']
        messages.success(request, "Vous avez été déconnecté avec succès.")
    
    return redirect('accueil')


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
        # Initialize request.client and request.user
        request.client = None
        request.user = AnonymousUser() # Initialize request.user to AnonymousUser

        if 'client_id' in request.session:
            try:
                client = Client.objects.get(id=request.session['client_id'])
                
                # Vérifier si le compte est actif
                if not client.actif:
                    # Déconnecter l'utilisateur si son compte a été désactivé
                    del request.session['client_id']
                    # Clear request.client and set request.user back to AnonymousUser
                    request.client = None
                    request.user = AnonymousUser()
                    messages.error(
                        request, 
                        "Votre compte a été désactivé. Veuillez contacter l'administrateur."
                    )
                    # Do not redirect here, let the view/decorator handle it after middleware
                    # return redirect('login') # Removed redirection from middleware

                else:
                     # Attacher le client à l'objet request
                     request.client = client
                     # Set request.user for compatibility with Django's auth system
                     request.user = client # Assuming Client model has necessary properties

            except Client.DoesNotExist:
                # Déconnecter si l'ID du client n'existe pas
                del request.session['client_id']
                # Clear request.client and set request.user back to AnonymousUser
                request.client = None
                request.user = AnonymousUser()
                # Do not redirect here, let the view/decorator handle it after middleware
                # return redirect('login') # Removed redirection from middleware
        
        # If no client_id in session, request.client is None and request.user is already AnonymousUser

        response = get_response(request)
        return response
    
    return middleware


