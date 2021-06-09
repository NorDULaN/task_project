"""Cart-related views."""
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse

from .forms import ReplaceCartLineForm
from ..order import OrderStatus
from ..order.models import Order, OrderLine
from ..product.models import ProductVariant, Category
from .models import Cart
from .utils import (check_product_availability_and_warn, get_cart_data,
                    get_or_empty_db_cart)


@get_or_empty_db_cart(cart_queryset=Cart.objects.for_display())
def index(request, cart):
    """Display cart details."""
    cart_lines = []

    try:
        cart = Cart.objects.get(pk=cart.pk)
    except Cart.DoesNotExist:
        pass

    for line in cart.lines.all():
        initial = {'quantity': line.quantity}
        form = ReplaceCartLineForm(None, cart=cart, variant=line.variant,
                                   initial=initial)
        line.variant.category_name = line.variant.get_category_name()
        cart_lines.append({
            'quantity': line.quantity,
            'variant': line.variant,
            'get_price_per_item': line.get_price_per_item(),
            'get_total': line.get_total(),
            'form': form,
            'photo': "/img.png"
        })

    cart_data = get_cart_data(cart)

    ctx = {
        'cart': cart,
        'cart_lines': cart_lines,
    }

    ctx.update(cart_data)
    return TemplateResponse(
        request, 'cart.html', ctx)


@get_or_empty_db_cart()
def update(request, cart, variant_id):
    """Update the line quantities."""
    if not request.is_ajax():
        return redirect('cart:index')
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    status = None
    form = ReplaceCartLineForm(
        request.POST, cart=cart, variant=variant)
    if form.is_valid():
        form.save()
        response = {
            'variantId': variant_id,
            'subtotal': 0,
            'total': 0,
            'cart': {
                'numItems': cart.quantity,
                'numLines': len(cart)}}
        updated_line = cart.get_line(form.cart_line.variant)
        if updated_line:
            response['subtotal'] = updated_line.get_total()
        if cart:
            cart_total = cart.get_total()
            response['total'] = cart_total
            local_cart_total = cart_total
            if local_cart_total is not None:
                response['localTotal'] = local_cart_total
        status = 200
    elif request.POST is not None:
        response = {'error': form.errors}
        status = 400
    cart.clear_promocode()
    return JsonResponse(response, status=status)
