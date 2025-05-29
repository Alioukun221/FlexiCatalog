from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    ReferenceField, EmbeddedDocumentField, IntField,
    StringField, DateTimeField, EmbeddedDocumentListField, ListField, DecimalField
)
from django.contrib.auth.models import User
from Users.models import Client
from produits.models import Produit
from datetime import datetime


class Cart(Document):
    user = ReferenceField(Client, required=False) 
    session_key = StringField(required=False) 
    items = ListField(ReferenceField('CartItem'))
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)
    
    @property
    def total_price(self):
        return sum(item.product.prix * item.quantity for item in self.items)

class CartItem(Document):
    cart = ReferenceField('Cart', reverse_delete_rule=2)  # 2 = CASCADE
    product = ReferenceField('Produit')
    quantity = IntField(default=1)
    
    @property
    def total_price(self):
        return self.product.prix * self.quantity


class Order(Document):
    user = ReferenceField(Client, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    total_price = DecimalField(required=True, precision=2)
    # Add other relevant fields like payment status, shipping address, etc.

class OrderItem(EmbeddedDocument):
    product = ReferenceField(Produit, required=True)
    quantity = IntField(required=True)
    price = DecimalField(required=True, precision=2) # Price per unit at the time of order


# Add items list to Order model
Order.items = EmbeddedDocumentListField(OrderItem)


