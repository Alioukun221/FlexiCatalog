from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from produits.models import Produit
from .models import Cart, CartItem, Order, OrderItem
from django.views.generic import View
from django.http import JsonResponse
from mongoengine.errors import DoesNotExist


def get_or_create_cart(request):
    # Créer la session si elle n'existe pas encore
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # Check if the custom authenticated client is available
    if request.client:
        # Chercher un panier lié à l'utilisateur authentifié (request.client)
        cart = Cart.objects(user=request.client).first()
        if not cart:
            # Créer un panier lié à l'utilisateur authentifié
            cart = Cart(user=request.client, session_key=session_key) # Keep session_key for potential merging later
            cart.save()
    else:
        # Utilisateur anonyme
        cart = Cart.objects(session_key=session_key).first()
        if not cart:
            # Créer un panier avec session_key obligatoire
            cart = Cart(session_key=session_key)
            cart.save()

    # Ensure the session key is always set on the cart if the cart was just created for an authenticated user
    # This helps in the login view's cart migration logic.
    if request.client and cart and not cart.session_key:
         cart.session_key = session_key
         cart.save()

    return cart



@require_POST
def add_to_cart(request, product_slug):


    try:
        # Récupération du produit
        product = Produit.objects.get(slug=product_slug)

        # Vérification de la quantité
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Quantité invalide'
            }, status=400)

        if quantity < 1:
            return JsonResponse({
                'success': False,
                'message': 'La quantité doit être au moins 1.'
            }, status=400)

        if product.stock < quantity:
            return JsonResponse({
                'success': False,
                'message': f'Stock insuffisant. Disponible: {product.stock}'
            }, status=400)

        # Récupération ou création du panier
        cart = get_or_create_cart(request)

        # Récupération ou création de l'article dans le panier
        cart_item = CartItem.objects(cart=cart, product=product).first()
        if not cart_item:
            cart_item = CartItem(cart=cart, product=product, quantity=quantity)
        else:
            cart_item.quantity += quantity
        cart_item.save()

        # Calcul des totaux
        cart_items = CartItem.objects(cart=cart)
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.product.prix * item.quantity for item in cart_items)

        return JsonResponse({
            'success': True,
            'message': f'{product.nom} ajouté au panier',
            'cart_total_items': total_items,
            'cart_total_price': float(total_price),
            'item_quantity': cart_item.quantity
        })

    except Produit.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Produit non trouvé'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Une erreur est survenue : {str(e)}'
        }, status=500)


def cart_detail(request):
    """Afficher le contenu du panier"""
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects(cart=cart)

    # Calcul des totaux
    total_items = 0
    total_price = 0
    
    for item in cart_items:
        total_items += item.quantity
        total_price += item.product.prix * item.quantity

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price,
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def update_cart_item(request, item_id):
    """Mettre à jour la quantité d'un item dans le panier"""
    cart = get_or_create_cart(request)
    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        if quantity <= 0:
            cart_item.delete()
            message = f'{cart_item.product.nom} retiré du panier'
        else:
            if quantity > cart_item.product.stock:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Stock insuffisant. Disponible: {cart_item.product.stock}'
                    })
                messages.error(request, f'Stock insuffisant pour {cart_item.product.nom}')
                return redirect('cart:cart_detail')
            
            cart_item.quantity = quantity
            cart_item.save()
            message = f'Quantité mise à jour pour {cart_item.product.nom}'
        
        # Recalculer les totaux après mise à jour
        cart_items = CartItem.objects(cart=cart)
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.product.prix * item.quantity for item in cart_items)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_total_items': total_items,
                'cart_total_price': float(total_price),
                'item_total_price': float(cart_item.product.prix * cart_item.quantity) if quantity > 0 else 0
            })
        
        messages.success(request, message)
        return redirect('cart:cart_detail')
        
    except CartItem.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Article non trouvé dans le panier'
            }, status=404)
        messages.error(request, 'Article non trouvé dans le panier')
        return redirect('cart:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    """Supprimer un item du panier"""
    cart = get_or_create_cart(request)
    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        product_name = cart_item.product.nom
        cart_item.delete()
        
        # Recalculer les totaux après suppression
        cart_items = CartItem.objects(cart=cart)
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.product.prix * item.quantity for item in cart_items)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product_name} retiré du panier',
                'cart_total_items': total_items,
                'cart_total_price': float(total_price)
            })
        
        messages.success(request, f'{product_name} a été retiré de votre panier.')
        return redirect('cart:cart_detail')
        
    except CartItem.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Article non trouvé dans le panier'
            }, status=404)
        messages.error(request, 'Article non trouvé dans le panier')
        return redirect('cart:cart_detail')


def clear_cart(request):
    """Vider complètement le panier"""
    cart = get_or_create_cart(request)
    CartItem.objects(cart=cart).delete()  # suppression des items du panier
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Panier vidé'
        })
    
    messages.success(request, 'Votre panier a été vidé.')
    return redirect('cart:cart_detail')


def cart_count(request):
    """API pour obtenir le nombre d'items dans le panier"""
    cart = get_or_create_cart(request)
    return JsonResponse({
        'count': cart.total_items,
        'total_price': float(cart.total_price)
    })


class CartCountView(View):
    def get(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        return JsonResponse({
            'count': cart.total_items,
            'total': float(cart.total_price)
        })

@login_required # Ensure user is logged in to access this page
def wave_payment_view(request):
    """View for the Wave payment page."""
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects(cart=cart)

    if not cart_items:
        messages.warning(request, "Votre panier est vide.")
        return redirect('cart:cart_detail')

    total_price = sum(item.product.prix * item.quantity for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart/wave_payment.html', context)

@require_POST # Only allow POST requests for payment processing
@login_required # Ensure user is logged in to process payment
def process_wave_payment(request):
    """View to process Wave payment and finalize the order."""
    user = request.client # Get the authenticated user from the request (thanks to middleware)
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects(cart=cart)

    if not cart_items:
        messages.error(request, "Impossible de passer la commande, votre panier est vide.")
        return redirect('cart:cart_detail')

    # Calculate total price again to ensure accuracy
    total_price = sum(item.product.prix * item.quantity for item in cart_items)

    # --- Payment Simulation ---
    # In a real integration, you would interact with the Wave API here.
    # This is a placeholder to simulate a successful payment.
    payment_successful = True # Assume payment is successful for now
    # --- End Payment Simulation ---

    if payment_successful:
        try:
            # Create a new Order
            order = Order(user=user, total_price=total_price)

            # Create OrderItems from CartItems and update product stock
            order_items_list = []
            for cart_item in cart_items:
                product = cart_item.product

                # Check stock again before finalizing (important!)
                if product.stock < cart_item.quantity:
                    messages.error(request, f'Stock insuffisant pour {product.nom}. Veuillez ajuster votre panier.')
                    # Optionally, update the cart quantity to max available stock
                    # cart_item.quantity = product.stock
                    # cart_item.save()
                    # return redirect('cart:cart_detail')
                    raise Exception(f'Stock insuffisant pour {product.nom}') # Or handle this differently

                # Create OrderItem
                order_item = OrderItem(
                    product=product,
                    quantity=cart_item.quantity,
                    price=product.prix # Use the price at the time of order
                )
                order_items_list.append(order_item)

                # Update product stock
                product.stock -= cart_item.quantity
                product.save()

            # Add items to the order and save the order
            order.items = order_items_list
            order.save()

            # Clear the user's cart after successful order
            cart_items.delete()

            messages.success(request, "Votre commande a été passée avec succès!")
            # Redirect to an order confirmation page
            return redirect('order_success') # You'll need to define this URL name

        except Exception as e:
            # Handle potential errors during order creation or stock update
            messages.error(request, f'Une erreur est survenue lors du traitement de votre commande : {e}')
            return redirect('cart:cart_detail')

    else:
        # Handle failed payment (in a real scenario)
        messages.error(request, "Le paiement a échoué. Veuillez réessayer.")
        return redirect('cart:cart_detail')

def order_success_view(request):
    """View for the order success page."""
    return render(request, 'cart/order_success.html')
