from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from produits.models import Produit
from .models import Cart, CartItem
from django.views.generic import View
from django.http import JsonResponse
from mongoengine.errors import DoesNotExist


def get_or_create_cart(request):
    # Créer la session si elle n'existe pas encore
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:
        # Chercher un panier lié à l'utilisateur
        cart = Cart.objects(user_id=str(request.user.id)).first()
        if not cart:
            # Créer un panier avec user_id et session_key (session_key obligatoire)
            cart = Cart(user_id=str(request.user.id), session_key=session_key)
            cart.save()
    else:
        # Utilisateur anonyme
        cart = Cart.objects(session_key=session_key).first()
        if not cart:
            # Créer un panier avec session_key obligatoire
            cart = Cart(session_key=session_key)
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
    cart_items = CartItem.objects(cart=cart)  # correction ici pour récupérer les items liés au panier

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def update_cart_item(request, item_id):
    """Mettre à jour la quantité d'un item dans le panier"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
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
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price),
            'item_total_price': float(cart_item.total_price) if quantity > 0 else 0
        })
    
    messages.success(request, message)
    return redirect('cart:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    """Supprimer un item du panier"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    product_name = cart_item.product.nom
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product_name} retiré du panier',
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price)
        })
    
    messages.success(request, f'{product_name} a été retiré de votre panier.')
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
