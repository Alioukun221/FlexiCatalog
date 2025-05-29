from django.urls import path
from . import views
from .views import CartCountView

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<slug:product_slug>/', views.add_to_cart, name='add_to_cart'),
    path('update/<str:item_id>/', views.update_cart_item, name='update_item'),
    path('remove/<str:item_id>/', views.remove_from_cart, name='remove_item'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('count/', views.cart_count, name='cart_count'),
    path('api/count/', CartCountView.as_view(), name='cart_count_api'),
    path('wave-payment/', views.wave_payment_view, name='wave_payment'),
    path('process-payment/', views.process_wave_payment, name='process_wave_payment'),
    path('order-success/', views.order_success_view, name='order_success'),
]