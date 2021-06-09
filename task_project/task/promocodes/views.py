from django.http import JsonResponse
from django.template.response import TemplateResponse

from ..cart.models import Cart
from ..cart.utils import get_or_empty_db_cart
from .models import Promocode


@get_or_empty_db_cart(cart_queryset=Cart.objects.for_display())
def add_promocode_to_cart(request, cart):

    promocode = request.GET.get('promocode')
    if not promocode:
        return JsonResponse({
            'status': 'failed',
            'msg': "Bad param"
        })

    promocodes = Promocode.objects.values('pk', 'code_variants')
    promo_pk = None
    for promo_el in promocodes:
        variants = promo_el['code_variants'].replace(' ', '').split(',')
        for variant in variants:
            if variant == promocode:
                promo_pk = promo_el['pk']

    promo = Promocode.objects.filter(pk=promo_pk).first()
    if promo is None:
        return JsonResponse({
            'status': 'failed',
            'msg': "Not exist"
        })

    variants_ids = set(cart.lines.values_list('variant_id', flat=True))

    is_valid, error = promo.is_valid(user=request.user, order_sum=cart.get_total(), variants_ids=variants_ids)
    msg = error

    if error == '__promocode__error__min_order_sum__':
        msg += ' {} {}'.format(promo.min_order_sum - cart.get_total(), "₴")

    if not is_valid:
        status = 'failed'
    else:
        status = 'success'
        cart.promocode = promo
        cart.save()

    return JsonResponse({
        'status': status,
        'msg': msg,
        'saved_money': round(cart.get_saved_money_via_promocode(), 2),
        'cart_total': round(cart.get_total(), 2)
    })

@get_or_empty_db_cart(cart_queryset=Cart.objects.for_display())
def remove_promocode(request, cart):
    promocode = request.GET.get('promocode')
    cart.promocode = None
    cart.save()

    return JsonResponse({
        'status': "success",
    })