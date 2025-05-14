from django.urls import path
from .views import *

urlpatterns = [
   path('' , add_user),
   path('update/' , update),
   path('delete_user/', delete_user),
]
