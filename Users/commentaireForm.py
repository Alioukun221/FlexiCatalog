from django import forms
from .models import Commentaire

class CommentaireForm(forms.Form):
    user_nom = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Votre nom'
        })
    )
    user_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Votre email'
        })
    )
    note = forms.ChoiceField(
        choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')],
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    contenu = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 4,
            'placeholder': 'Votre commentaire...'
        })
    )