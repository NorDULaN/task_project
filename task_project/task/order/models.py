from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from . import GroupStatus, OrderStatus, OrderType

from ..product.models import ProductVariant
from ..promocodes.models import Promocode


class OrderQuerySet(models.QuerySet):
    """Filters orders by status deduced from shipment groups."""

    def open(self):
        """Orders having at least one shipment group with status NEW."""
        return self.filter(Q(groups__status=GroupStatus.NEW))

    def all(self):
        return self

    def all_minus_test(self):
        return self.filter(~Q(status='test'))

    def closed(self):
        """Orders having no shipment groups with status NEW."""
        return self.filter(~Q(groups__status=GroupStatus.NEW))

    def filter_by_status(self, status='all_without_test'):
        """Orders having no shipment groups with status NEW."""
        return self.filter(Q(status=status))


class Order(models.Model):
    created = models.DateTimeField(
        default=now,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='orders',
        on_delete=models.SET_NULL)
    tracking_client_id = models.CharField(
        max_length=36, blank=True, editable=False)
    user_email = models.EmailField(
        blank=True, default='', editable=False)
    shipping_price_net = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0, editable=False)
    shipping_price_gross = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0, editable=False)
    shipping_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    token = models.CharField(max_length=36, unique=True)
    total_net = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True)
    total_gross = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True)
    discount_name = models.CharField(max_length=255, default='', blank=True)

    status = models.CharField(
        max_length=128,
        choices=OrderStatus.CHOICES,
        default=OrderStatus.CHOICES[0][0]
    )
    tracking_number = models.CharField(max_length=255, default='', blank=True)
  
    pre_order_user_phone = models.CharField(max_length=20, default='', blank=True)

    promocode = models.ForeignKey(Promocode, blank=True, null=True, on_delete=models.SET_NULL)
    promocode_saved_money = models.DecimalField(default=0, max_digits=12, decimal_places=2, blank=True)

    nip = models.CharField(max_length=255, default='')

    objects = OrderQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid4())
        return super().save(*args, **kwargs)

    def get_lines(self):
        return OrderLine.objects.filter(delivery_group__order=self)

    def is_fully_paid(self):
        total_paid = sum(
            [
                payment.get_total_price() for payment in
                self.payments.filter(status=PaymentStatus.CONFIRMED)],
            0)
        return total_paid >= self.total

    def get_user_current_email(self):
        return self.user.email if self.user else self.user_email

    def _index_billing_phone(self):
        return self.billing_address.phone

    def _index_shipping_phone(self):
        return self.shipping_address.phone

    def __iter__(self):
        return iter(self.groups.all())

    def __repr__(self):
        return '<Order #%r>' % (self.id,)

    def __str__(self):
        return '№ {0:,}'.format(self.id,).replace(',', ' ')

    def get_absolute_url(self):
        return reverse('order:details', kwargs={'token': self.token})

    def get_last_payment_status(self):
        last_payment = self.payments.last()
        if last_payment:
            return last_payment.status
        return None

    def get_last_payment_status_display(self):
        last_payment = self.payments.last()
        if last_payment:
            return last_payment.get_status_display()
        return None

    def is_pre_authorized(self):
        return self.payments.filter(status=PaymentStatus.PREAUTH).exists()

    def is_shipping_required(self):
        return any(group.is_shipping_required() for group in self.groups.all())

    @property
    def is_open(self):
        return self.status == OrderStatus.OPEN

    def get_status_display(self):
        """Order status display text."""
        return dict(OrderStatus.CHOICES)[self.status]

    def get_subtotal(self):
        subtotal_iterator = (line.get_total() for line in self.get_lines())
        return sum(subtotal_iterator, 0)

    def can_cancel(self):
        return self.status == OrderStatus.OPEN

    def get_user_full_name(self):
        if self.billing_address and (self.billing_address.first_name or self.billing_address.last_name):
            full_name = '{} {}'.format(
                self.billing_address.first_name,
                self.billing_address.last_name
            )
        elif self.user is not None:
            full_name = '{} {}'.format(
                self.user.first_name if self.user is not None else '',
                self.user.last_name if self.user is not None else ''
            )
        else:
            full_name = 'Guest'
        return full_name

    def get_first_and_last_user_name(self):
        if self.billing_address and self.billing_address.first_name:
            first_name = self.billing_address.first_name
            last_name = self.billing_address.last_name
        elif self.user is not None:
            first_name = self.user.first_name
            last_name = self.user.last_name
        else:
            first_name = 'Guest'
            last_name = ''
        return first_name, last_name

    def get_user_email(self):
        if self.user is not None:
            email = '{}'.format(self.user.email if self.user is not None else '')
        elif self.user_email:
            email = self.user_email
        else:
            email = 'Guest'
        return email

    def get_user_phone(self):
        if self.billing_address and self.billing_address.phone:
            return str(self.billing_address.phone)
        elif self.user is not None:
            address = self.user.addresses.order_by('-id').last()
            if address is not None:
                return str(address.phone)
            else:
                return ''
        elif self.pre_order_user_phone:
            return str(self.pre_order_user_phone)
        else:
            return 'Guest'

    def get_type(self):
        if self.status == OrderStatus.PRE_ORDER:
            return OrderType.PRE_ORDER
        elif self.status == OrderStatus.ONE_CLICK:
            return OrderType.ONE_CLICK
        else:
            return OrderType.TYPICAL

    def get_status_color(self):
        colors = {
            OrderStatus.OPEN: '#77e683',
            OrderStatus.CLOSED: '#d0d0d0',
            OrderStatus.CANCELED: '#ffadaf',
            OrderStatus.HOLD: '#e6e64a',
            OrderStatus.SHIPPED: '#c49bd8',
            OrderStatus.TEST: '#d0d0d0',
            OrderStatus.PRE_ORDER: '#e6e64a',
            OrderStatus.ONE_CLICK: '#e6e64a',
            OrderStatus.NO_ANSWER: '#ffba00',
            OrderStatus.SEND_TO_DEALER: '#c49bd8',
            OrderStatus.CALL_BACK_REQUEST: '#665CAC',
        }
        color = colors.get(self.status, '#d0d0d0')
        return color


class OrderLine(models.Model):
    product = models.ForeignKey(
        ProductVariant, blank=True, null=True, related_name='+',
        on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=128)
    is_shipping_required = models.BooleanField()
    stock_location = models.CharField(max_length=100, default='')
    stock = models.ForeignKey(
        'product.Stock', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(999)])
    unit_price_net = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True)
    unit_price_gross = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.product_name

    def get_total(self):
        return self.unit_price * self.quantity

    def get_sku(self):
        sku = ''
        return sku




