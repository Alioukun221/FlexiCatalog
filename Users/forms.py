from django import forms
from .models import Client, PasswordResetToken
import re
from datetime import datetime, timedelta
from django.utils import timezone
import secrets

class ClientRegistrationForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur", 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label="Confirmez le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Client.objects(username=username):
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Client.objects(email=email):
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        # Vérifier que le mot de passe contient au moins une lettre et un chiffre
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre et un chiffre.")
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data

    def save(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        client = Client(
            username=username,
            email=email,
            role='client',
            date_inscription=datetime.now(),
            actif=True
        )
        client.set_password(password)
        client.save()
        
        return client


class ClientLoginForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur ou Email",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            # Vérifier si l'utilisateur existe (par username ou email)
            client = None
            if '@' in username:
                client = Client.objects(email=username).first()
            else:
                client = Client.objects(username=username).first()
            
            if not client or not client.check_password(password):
                raise forms.ValidationError("Nom d'utilisateur ou mot de passe incorrect.")
            
            if not client.actif:
                raise forms.ValidationError("Ce compte a été désactivé.")
                
            cleaned_data['client'] = client
        
        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        client = Client.objects(email=email).first()
        
        if not client:
            raise forms.ValidationError("Aucun compte n'est associé à cette adresse email.")
        
        self.client = client
        return email
    
    def generate_token(self):
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        
        # Invalider les tokens précédents pour ce client
        PasswordResetToken.objects(client=self.client, used=False).update(used=True)
        
        # Créer un nouveau token
        reset_token = PasswordResetToken(
            client=self.client,
            token=token,
            expires_at=expires_at
        )
        reset_token.save()
        
        return reset_token

class PasswordResetConfirmForm(forms.Form):
    password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label="Confirmez le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, token=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_obj = None
        
        if token:
            self.token_obj = PasswordResetToken.objects(
                token=token,
                used=False,
                expires_at__gt=timezone.now()
            ).first()
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre et un chiffre.")
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not self.token_obj:
            raise forms.ValidationError("Ce lien de réinitialisation est invalide ou a expiré.")
        
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data
    
    def save(self):
        client = self.token_obj.client
        client.set_password(self.cleaned_data['password'])
        client.save()
        
        self.token_obj.used = True
        self.token_obj.save()
        
        return client
    
    
class ClientProfileUpdateForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur", 
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, client=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        
        if client:
            self.fields['username'].initial = client.username
            self.fields['email'].initial = client.email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username != self.client.username and Client.objects(username=username):
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != self.client.email and Client.objects(email=email):
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email
    
    def save(self):
        self.client.username = self.cleaned_data.get('username')
        self.client.email = self.cleaned_data.get('email')
        self.client.save()
        
        return self.client


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Mot de passe actuel",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password_confirm = forms.CharField(
        label="Confirmez le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, client=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.client.check_password(current_password):
            raise forms.ValidationError("Mot de passe incorrect.")
        return current_password
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if len(new_password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        # Vérifier que le mot de passe contient au moins une lettre et un chiffre
        if not re.search(r'[A-Za-z]', new_password) or not re.search(r'\d', new_password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre et un chiffre.")
        
        return new_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        
        if new_password and new_password_confirm and new_password != new_password_confirm:
            self.add_error('new_password_confirm', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data
    
    def save(self):
        self.client.set_password(self.cleaned_data.get('new_password'))
        self.client.save()
        
        return self.client