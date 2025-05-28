from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    ReferenceField, EmbeddedDocumentField, IntField,
    StringField, DateTimeField, EmbeddedDocumentListField, ListField,
)
from django.contrib.auth.models import User
from produits.models import Produit  # Assurez-vous que ce modèle est aussi basé sur mongoengine
from datetime import datetime


class Cart(Document):
    user_id = StringField()
    session_key = StringField(required=True)
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


