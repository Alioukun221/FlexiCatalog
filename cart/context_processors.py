from .models import Cart, CartItem
from .views import get_or_create_cart

def cart_context(request):
    """Context processor to add cart information to the context."""
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects(cart=cart)
    total_items = sum(item.quantity for item in cart_items)
    return {
        'cart_total_items': total_items,
    }