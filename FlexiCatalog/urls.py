
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('', include('accueil.urls')),
    path('produits/', include('produits.urls')),
    path('admin/', include('admindashboard.urls')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('',include('Users.urls')),
]


