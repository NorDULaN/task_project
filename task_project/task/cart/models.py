"""Cart-related ORM models."""
from collections import namedtuple
from decimal import Decimal
from itertools import groupby
from uuid import uuid4

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.encoding import smart_str
from django.utils.timezone import now

import functools
import operator
from typing import Iterable, TypeVar
T = TypeVar('T')
def sum_prices(values: Iterable[T]) -> T:
    """Return a sum of given values."""
    return functools.reduce(operator.add, values)


from . import CartStatus, logger
from ..promocodes.models import Promocode

CENTS = Decimal('0.01')
SimpleCart = namedtuple('SimpleCart', ('quantity', 'total', 'token'))


def find_open_cart_for_user(user):
    """Find an open cart for the given user."""
    carts = user.carts.open()
    if len(carts) > 1:
        logger.warning('%s has more than one open basket', user)
        for cart in carts[1:]:
            cart.change_status(CartStatus.CANCELED)
    return carts.first()


class ProductGroup(list):
    """A group of products."""

    def is_shipping_required(self):
        """Return `True` if any product in group requires shipping."""
        return any(p.is_shipping_required() for p in self)

    def get_total(self):
        subtotals = [line.get_total() for line in self]
        if not subtotals:
            raise AttributeError(
                'Calling get_total() on an empty product group')
        return sum_prices(subtotals)


class CartQueryset(models.QuerySet):
    """A specialized queryset for dealing with carts."""

    def anonymous(self):
        """Return unassigned carts."""
        return self.filter(user=None)

    def open(self):
        """Return `OPEN` carts."""
        return self.filter(status=CartStatus.OPEN)

    def canceled(self):
        """Return `CANCELED` carts."""
        return self.filter(status=CartStatus.CANCELED)

    def for_display(self):
        """Annotate the queryset for display purposes.

        Prefetches additional data from the database to avoid the n+1 queries
        problem.
        """
        return self.prefetch_related(
            'lines__variant__product__category',
            'lines__variant__stock')


class Cart(models.Model):
    """A shopping cart."""

    status = models.CharField(
        max_length=32, choices=CartStatus.CHOICES, default=CartStatus.OPEN)
    created = models.DateTimeField(auto_now_add=True)
    last_status_change = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='carts',
        on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)
    token = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    promocode = models.ForeignKey(Promocode, blank=True, null=True, related_name='carts', on_delete=models.SET_NULL)

    objects = CartQueryset.as_manager()

    class Meta:
        ordering = ('-last_status_change',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clear_promocode(self):
        if self.promocode is not None:
            self.promocode = None
            self.save()

    def get_saved_money_via_promocode(self):

        saved_sum = 0

        if self.promocode is not None:

            rest = self.promocode.amount

            for line in self.lines.all():
                if self.promocode.from_base_price:
                    total_line = line.get_total_without_sale()
                else:
                    total_line = line.get_total()
                saved, rest = self.promocode.get_saved_money(variant=line.variant, total=total_line, rest=rest)
                saved_sum += saved

        return saved_sum

    def get_active_sales(self):
        sales = []
        if self.promocode is not None and self.promocode.from_base_price:
            return sales
        for line in self.lines.all():
            active_sales = line.variant.get_active_sales()
            if active_sales:
                for sale in active_sales:
                    sales.append(sale)
        return sales

    def get_active_sales_v2(self):
        sales = []
        for line in self.lines.all():
            active_sales = line.variant.get_active_sales()
            if active_sales:
                for sale in active_sales:
                    sales.append(sale)
        return sales

    def update_quantity(self):
        """Recalculate cart quantity based on lines."""
        total_lines = self.count()['total_quantity']
        if not total_lines:
            total_lines = 0
        self.quantity = total_lines
        self.save(update_fields=['quantity'])

    def change_status(self, status):
        """Change cart status."""
        # FIXME: investigate replacing with django-fsm transitions
        if status not in dict(CartStatus.CHOICES):
            raise ValueError('Not expected status')
        if status != self.status:
            self.status = status
            self.last_status_change = now()
            self.save()

    def change_user(self, user):
        """Assign cart to a user.

        If the user already has an open cart assigned, cancel it.
        """
        open_cart = find_open_cart_for_user(user)
        if open_cart is not None:
            open_cart.change_status(status=CartStatus.CANCELED)
        self.user = user
        self.save(update_fields=['user'])

    def is_shipping_required(self):
        """Return `True` if any of the lines requires shipping."""
        return any(line.is_shipping_required() for line in self.lines.all())

    def __repr__(self):
        return 'Cart(quantity=%s)' % (self.quantity,)

    def __len__(self):
        return self.lines.count()

    def get_total(self, without_promocode=False):
        """Return the total cost of the cart prior to shipping."""
        subtotals = [line.get_total() for line in self.lines.all()]
        if not subtotals:
            return 0
        cart_total = sum_prices(subtotals)
        if not without_promocode and self.promocode is not None:
            if self.promocode.from_base_price:
                cart_total = self.get_total_without_sales()
            return cart_total - self.get_saved_money_via_promocode()
        else:
            return cart_total

    def get_base_total(self):
        subtotals = [line.get_total_without_sale() for line in self.lines.all()]
        return sum_prices(subtotals)

    def get_total_without_promocode(self):
        return self.get_total(without_promocode=True)

    def get_total_without_sales(self):
        subtotals = [line.get_total_without_sale() for line in self.lines.all()]
        if not subtotals:
            return 0
        return sum_prices(subtotals)

    def get_sales_amount(self):
        return self.get_total_without_sales() - sum(line.get_total() for line in self.lines.all())

    def count(self):
        """Return the total quantity in cart."""
        lines = self.lines.all()
        return lines.aggregate(total_quantity=models.Sum('quantity'))

    def clear(self):
        """Remove the cart."""
        self.delete()

    def create_line(self, variant, quantity, data):
        """Create a cart line for given variant, quantity and optional data.

        The `data` parameter may be used to differentiate between items with
        different customization options.
        """
        return self.lines.create(
            variant=variant, quantity=quantity, data=data or {})

    def get_line(self, variant, data='{}'):
        """Return a line matching the given variant and data if any."""
        all_lines = self.lines.all()
        if data is None:
            data = {}
        line = [
            line for line in all_lines
            if line.variant_id == variant.id and line.data == data]
        if line:
            return line[0]
        return None

    def get_line_refresh(self, variant, data=None):
        """Return a line matching the given variant and data if any. (with no cache)"""
        all_lines = self.lines.filter()
        if data is None:
            data = {}
        line = [
            line for line in all_lines
            if line.variant_id == variant.id and line.data == data]
        if line:
            return line[0]
        return None

    def add(self, variant, quantity=1, data=None, replace=False,
            check_quantity=True, color=None):
        """Add a product vartiant to cart.

        The `data` parameter may be used to differentiate between items with
        different customization options.

        If `replace` is truthy then any previous quantity is discarded instead
        of added to.
        """
        cart_line, dummy_created = self.lines.get_or_create(
            variant=variant, defaults={'quantity': 0, 'data': data or {}})
        if replace:
            new_quantity = quantity
        else:
            new_quantity = cart_line.quantity + quantity

        if new_quantity < 0:
            raise ValueError('%r is not a valid quantity (results in %r)' % (
                quantity, new_quantity))

        if check_quantity:
            variant.check_quantity(new_quantity)

        cart_line.quantity = new_quantity

        if not cart_line.quantity:
            cart_line.delete()
        else:
            cart_line.save(update_fields=['quantity'])

        if color is not None:
            cart_line.color = color
            cart_line.save()

        self.update_quantity()

    def partition(self):
        """Split the cart into a list of groups for shipping."""
        grouper = (
            lambda p: 'physical' if p.is_shipping_required() else 'digital')
        subject = sorted(self.lines.all(), key=grouper)
        for _, lines in groupby(subject, key=grouper):
            yield ProductGroup(lines)


class CartLine(models.Model):
    """A single cart line.

    Multiple lines in the same cart can refer to the same product variant if
    their `data` field is different.
    """

    cart = models.ForeignKey(
        Cart, related_name='lines', on_delete=models.CASCADE)
    variant = models.ForeignKey(
        'product.ProductVariant', related_name='+', on_delete=models.CASCADE)
    data = models.TextField(blank=True)    
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(999)])

    class Meta:
        unique_together = ('cart', 'variant', 'data')

    def __str__(self):
        return smart_str(self.variant)

    def __eq__(self, other):
        if not isinstance(other, CartLine):
            return NotImplemented

        return (
            self.variant == other.variant and
            self.quantity == other.quantity and
            self.data == other.data)

    def __ne__(self, other):
        return not self == other  # pragma: no cover

    def __repr__(self):
        return 'CartLine(variant=%r, quantity=%r, data=%r)' % (
            self.variant, self.quantity, self.data)

    def __getstate__(self):
        return self.variant, self.quantity, self.data

    def __setstate__(self, data):
        self.variant, self.quantity, self.data = data

    def get_total(self):
        """Return the total price of this line."""
        try:
            amount = self.get_price_per_item() * self.quantity
        except:
            amount = Decimal('0.00')
        return amount.quantize(CENTS)

    def get_total_without_sale(self):
        try:
            amount = self.get_price_per_item_without_sale() * self.quantity
        except:
            amount = Decimal('0.00')
        return amount.quantize(CENTS)

    # pylint: disable=W0221
    def get_price_per_item(self):
        """Return the unit price of the line."""
        return self.variant.get_price_per_item()

    def get_price_per_item_without_sale(self):
        return self.variant.get_price_per_item(without_sale=True)

    def is_shipping_required(self):
        """Return `True` if the related product variant requires shipping."""
        return self.variant.is_shipping_required()
