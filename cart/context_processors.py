from .models import Cart

def cart_context(request):
    """Ajouter les infos du panier dans tous les templates"""
    cart = None
    cart_total_items = 0
    cart_total_price = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            pass
    else:
        if request.session.session_key:
            try:
                cart = Cart.objects.get(session_key=request.session.session_key)
            except Cart.DoesNotExist:
                pass
    
    if cart:
        cart_total_items = cart.total_items
        cart_total_price = cart.total_price
    
    return {
        'cart': cart,
        'cart_total_items': cart_total_items,
        'cart_total_price': cart_total_price
    }