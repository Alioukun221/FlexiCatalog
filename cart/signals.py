from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem

@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    """Fusionner le panier anonyme avec le panier utilisateur lors de la connexion"""
    if request.session.session_key:
        try:
            # Récupérer le panier anonyme
            anonymous_cart = Cart.objects.get(session_key=request.session.session_key)
            
            # Récupérer ou créer le panier utilisateur
            user_cart, created = Cart.objects.get_or_create(user=user)
            
            # Fusionner les items
            for item in anonymous_cart.items.all():
                user_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=item.product,
                    defaults={'quantity': item.quantity}
                )
                
                if not created:
                    # Si l'item existe déjà, additionner les quantités
                    max_quantity = min(
                        user_item.quantity + item.quantity,
                        item.product.stock
                    )
                    user_item.quantity = max_quantity
                    user_item.save()
            
            # Supprimer le panier anonyme
            anonymous_cart.delete()
            
        except Cart.DoesNotExist:
            pass