from datetime import date

from django.db.models.signals import post_save
from django.utils.translation import pgettext_lazy
from django.db.models import Q
from django.dispatch import receiver

from django.db import models


class SaleManager(models.Manager):
    def get_active_sales(self):
        today = date.today()
        sales = self.filter(active=True, start_date__lte=today)
        return sales.filter(Q(end_date__gte=today) | Q(end_date__isnull=True)).order_by('priority')

    def get_actual_sale(self):
        return self.get_active_sales().first()


class Sale(models.Model):
    objects = SaleManager()

    choices_type = [
        ('fixed', 'Fixed amount from base price'),
        ('percentage', 'Amount - % from base price')
    ]
    name = models.CharField(max_length=255)
    name_display = models.ForeignKey('sale.DiscountName', default=None, null=True, help_text='Displayed in checkout', on_delete=models.SET_NULL)
    type = models.CharField(
        max_length=10, choices=choices_type,
        default=choices_type[0])
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    product = models.ForeignKey('product.ProductVariant', related_name='sales', on_delete=models.CASCADE)

    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)

    active = models.BooleanField(default=False)
    priority = models.SmallIntegerField(default=0)

    class Meta:
        permissions = (
            ('view_sale',
             pgettext_lazy('Permission description', 'Can view sales')),
            ('edit_sale',
             pgettext_lazy('Permission description', 'Can edit sales')))

    def __str__(self):
        return self.name

    def check_sale(self):
        today = date.today()
        if self.active and today >= self.start_date and (self.end_date is None or today <= self.end_date):
            return True
        return False

    def get_price(self):
        product_price = self.product.price_override if self.product.price_override else 0
        if self.check_sale():
            price = None
            if self.type == 'fixed':
                price = product_price - self.value
            elif self.type == 'percentage':
                base_price_percent = (product_price / 100) * self.value
                price = product_price - base_price_percent
                price = round(price, 2)
            return price
        return product_price


class DiscountName(models.Model):
    name = models.CharField(max_length=1024, blank=False)
    value = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    show_tag = models.BooleanField(default=False)
    gradient = models.TextField(default='', blank=True)
    COLOR_WHITE = '#ffffff'
    COLOR_BLACK = '#000000'
    COLORS = (
        (COLOR_WHITE, 'White text'),
        (COLOR_BLACK, 'Black text'),
    )
    tag_text_color = models.CharField(max_length=30, choices=COLORS, default=COLOR_BLACK)

    class Meta:
        ordering = ['order']
        verbose_name = 'Sale Name'

    def __str__(self):
        return self.name


@receiver(post_save, sender=DiscountName)
def discount_save(instance, *args, **kwargs):
    order = instance.order # сортировка единая на все языки
    DiscountName.objects.filter(name=instance.name).update(order=order)
