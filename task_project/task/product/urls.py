from django.conf.urls import url
from django.urls import path

from .views import *

urlpatterns = [
    url(r'^(?P<cat>[a-z0-9-_]+)/(?P<path>[a-zA-Z0-9-_]+)/?$',
        product_resolve, name='resolve'),
    url(r'^(?P<cat>[a-z0-9-_]+)/(?P<path>[a-zA-Z0-9-_]+)/add/$',
        add_to_cart, name='add-to-cart'),
    
]
