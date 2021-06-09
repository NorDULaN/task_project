from django.http import JsonResponse
from django.template.response import TemplateResponse

from ..cart.utils import set_cart_cookie, get_cart_from_request, get_or_create_cart_from_request
from ..product.models import Product, ProductVariant, Category


def main(request):
    cart = get_cart_from_request(request)
   
    maincat = Category.objects.filter(id_item=1).all()
    products = Product.objects.filter(category__in=maincat).order_by('name')
    variants = ProductVariant.objects.filter(is_active=True, product__in=products).exclude(
        status__in=[99, 3]
    ).order_by('priority')
   
    p = []
    for j, item_variant in enumerate(variants):
        pr = item_variant.product
        pr.variant = item_variant

        pr.price = None
        p.append(pr)

    ctx = {}
    ctx.update({
        'object': maincat, 
        "products": p, 
        'maincat': maincat,  
        'cart_lines': cart.lines.all().values_list('variant__name', flat=True), 
        'cart': cart
    })
    return TemplateResponse(request, 'index.html', ctx)