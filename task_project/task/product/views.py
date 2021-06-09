import json
from urllib.parse import urlencode
from django.conf import settings
from django.db.models import Max, Q
from django.http import (HttpResponsePermanentRedirect, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect
from django.template.defaultfilters import linebreaksbr
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import FormView

from .models import (Product, ProductVariant)

from ..cart.utils import set_cart_cookie, get_cart_from_request, \
    get_or_create_cart_from_request




def add_to_cart(request, cat, path):
    if not request.method == 'POST':
        return JsonResponse({'message': 'forbidden'}, status=403)

    product = get_object_or_404(ProductVariant, path=path)
    cart = get_or_create_cart_from_request(request)
    cart.clear_promocode()
    cart.add(product, 1, replace=True)

    ctx = {
        'message': 'success',
        'cart_counter': cart.lines.count(),
        'cart_url': reverse('cart:index')
    }
    response = JsonResponse(ctx, status=201)
    if not request.user.is_authenticated:
        set_cart_cookie(cart, response)
    return response
    
    
def product_resolve(request, path, cat=''):
   a = 1
