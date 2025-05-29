from django.urls import path
from .views import *
from .commentaire_views import * 

urlpatterns = [
   path('inscription/' , register_view ,name='register'),
   path('connexion/', login_view , name='login'),
   path('password_reset/' ,password_reset_request , name='reset_password' ),
   path('password_reset_confirm/<str:token>/', password_reset_confirm,name='password_reset_confirm'),
   path('profil_user/',profile , name='profile_user'),
   path('produit/<str:produit_id>/', detail_produit, name='detail_produit'),
   path('produit/<str:produit_id>/commentaires/', tous_commentaires_produit, name='commentaires_produit'),
   path('deconnexion/', logout, name='logout'),
]
