from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.validators import (
    MaxLengthValidator, MinValueValidator, RegexValidator)
from django.db import models
from django.db.models import F, Max, Q
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.translation import pgettext_lazy


class Category(models.Model):
    add_default = models.BooleanField(default=False)
    name = models.CharField(max_length=128)
    h1 = models.CharField(max_length=128, blank=True)
    slug = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    seo_title =  models.CharField(max_length=255, blank=True)
    seo_desc = models.CharField(max_length=1000, blank=True)
    seo_keys = models.CharField(max_length=255, blank=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        on_delete=models.CASCADE)
    id_item = models.IntegerField(null=True)
   

    objects = models.Manager()

    priority = models.IntegerField(default=0, blank=True)

    is_active = models.BooleanField(default=True)

    product_relations_title_localize = models.CharField(max_length=255, default='__product_relations__')

    installation = models.BooleanField(default=False)
    filter_registration = models.BooleanField(default=False)

    class Meta:
        app_label = 'product'
        permissions = (
            ('view_category',
             pgettext_lazy('Permission description', 'Can view categories')),
            ('edit_category',
             pgettext_lazy('Permission description', 'Can edit categories')),
            ('view_sku_global',
             pgettext_lazy('Permission description', 'Can view SKU')),
            ('edit_sku_global',
             pgettext_lazy('Permission description', 'Can edit SKU')),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product:cat',
                       kwargs={'path': self.get_full_path()
                               })
    def get_absolute_url_no_lang(self):
        return '/'+self.get_full_path()

    def get_full_path(self):
        return self.slug
    def get_full_path_locale(self):
        return LocaleUrl().get_locale_path(self)


class ProductType(models.Model):
    name = models.CharField(max_length=128)
    has_variants = models.BooleanField(default=True)
 
    is_shipping_required = models.BooleanField(default=False)

    class Meta:
        app_label = 'product'

    def __str__(self):
        return self.name

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)


class ProductQuerySet(models.QuerySet):
    def available_products(self, lang):
        return self.filter(
            Q(is_published=True), Q(lang=lang))


class Product(models.Model):
    product_type = models.ForeignKey(ProductType, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
   
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    ean_code = models.CharField(blank=True, default='', max_length=255)
    objects = ProductQuerySet.as_manager()

    class Meta:
        app_label = 'product'
        verbose_name = 'Product template'
        permissions = (
            ('view_product',
             pgettext_lazy('Permission description', 'Can view products')),
            ('edit_product',
             pgettext_lazy('Permission description', 'Can edit products')),
            ('view_properties',
             pgettext_lazy(
                 'Permission description', 'Can view product properties')),
            ('edit_properties',
             pgettext_lazy(
                 'Permission description', 'Can edit product properties')),
            ('brandquad_attr',
             pgettext_lazy('Permission description', 'Can access to Brandquad attributes')),
            ('banner_edit', pgettext_lazy('Permission description', 'Can edit product banners')),
            ('equipments_edit', pgettext_lazy('Permission description', 'Can edit product equipments')),
            ('tech_spec_edit', pgettext_lazy('Permission description', 'Can edit product tech specifications')),
            ('alt_cat_edit', pgettext_lazy('Permission description', 'Can edit product alt category')),
            ('files_edit', pgettext_lazy('Permission description', 'Can edit product files')),
            ('photo_add', pgettext_lazy('Permission description', 'Can add product photo')),
            ('photo_remove', pgettext_lazy('Permission description', 'Can remove product photo')),
            ('photo_change', pgettext_lazy('Permission description', 'Can change photo data on product')),
        )

    def __iter__(self):
        if not hasattr(self, '__variants'):
            setattr(self, '__variants', self.variants.all())
        return iter(getattr(self, '__variants'))

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)

    def __str__(self):
        return self.name

    def get_absolute_url(self, lang):
        return reverse(
            'product:resolve',
            kwargs={'path': self.get_slug(lang), 'cat': 'variant_not use'})

    def get_slug(self, lang):
        variant = self.variants.filter(lang=lang).first()
        return slugify(smart_text(variant.path))

    def get_first_image(self):
        first_image = self.images.first()
        return first_image.image if first_image else None

    def get_attribute(self, pk):
        return self.attributes.get(smart_text(pk))

    def set_attribute(self, pk, value_pk):
        self.attributes[smart_text(pk)] = smart_text(value_pk)

    def get_variant(self, lang):
        variant = ProductVariant.objects.all().filter(product_id=self.pk, lang=lang).first() or None
        if variant is not None:
            self.variant = variant
        else:
            self.variant = None

    def get_full_path_locale(self):
        return LocaleUrl().get_locale_path(self)

    def get_price_per_item(self, item, discounts=None):
        return item.get_price_per_item(discounts)

    def get_color_sku(self):
        sku = ColorVariation.objects.all().filter(parent=self)
        if sku.count() > 0:
            self.sku = sku
        else:
            self.sku = None

    def can_delete(self):
        return not self.variants.filter(~Q(lang='en'), is_active=True).exists()


class ProductVariant(models.Model):
    name = models.CharField(max_length=100, blank=False)
    status = models.PositiveSmallIntegerField(default=0)
    product = models.ForeignKey(
        Product, related_name='variants', on_delete=models.CASCADE)
    path = models.TextField()
    is_active = models.BooleanField(default=False)
    description = models.TextField(blank=True, default='')
    short_description = models.TextField(blank=True, default='', max_length=256)


    priority = models.IntegerField(default=1000, blank=True)

    price_override = models.DecimalField(max_digits=12, decimal_places=2,
        blank=True, null=True)
   
    show_in_discounts = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, blank=True,
                                        help_text='Product with the highest number will be the first in the list')
 

    class Meta:
        app_label = 'product'
        verbose_name = 'Product'

    def __str__(self):
        return self.name

  
    def get_category_name(self):
        category = Category.objects.filter(id_item=self.product.category.id).first()
        return category.name

    def get_category(self):
        category = Category.objects.filter(lang=self.lang, id_item=self.product.category.id).first()
        return category

    def check_quantity(self, quantity):
        total_available_quantity = self.get_stock_quantity()

    def get_stock_quantity(self):
        return sum([stock.quantity_available for stock in self.stock.all()])

    def get_sales(self):
        sale = self.sales.get_actual_sale()
        if sale:
            return sale if sale.check_sale() else None

    def get_absolute_url(self):
        slug = slugify(smart_text(self.path))
        cat_id = self.product.category.id_item
        cat_path = Category.objects.filter(id_item=cat_id).first() or None
        if not cat_path:
            cat_path = 'no_category'
        else:
            cat_path = cat_path.slug
        return reverse('product:resolve',
                       kwargs={'path': slug, 'cat': cat_path})

    def get_absolute_url_no_lang(self):
        slug = slugify(smart_text(self.path))
        cat_id = self.product.category.id_item
        cat_path = Category.objects.filter(id_item=cat_id, lang=self.lang).first() or None
        if not cat_path:
            cat_path = 'no_category'
        else:
            cat_path = cat_path.slug
        return '/'+cat_path+'/'+slug

    def get_full_path_locale(self):
        return LocaleUrl().get_locale_path(self)

    def as_data(self):
        return {
            'product_name': str(self),
            'product_id': self.product.pk,
            'variant_id': self.pk,
           }

   
    def display_product(self):
        variant_display = str(self)
        product_display = (
            '%s (%s)' % (self.product, variant_display)
            if variant_display else str(self.product))
        return smart_text(product_display)

    def get_first_image(self):
        return self.product.get_first_image()

    def get_price_per_item(self, without_sale=False):
        if not without_sale:
            sale = self.sales.get_actual_sale()
            if sale:
                return sale.get_price()
        return self.price_override

    def is_shipping_required(self):
        return self.product.product_type.is_shipping_required

    def select_stockrecord(self, quantity=1):
        # By default selects stock with lowest cost price. If stock cost price
        # is None we assume price equal to zero to allow sorting.
        stock = [
            stock_item for stock_item in self.stock.all()
            if stock_item.quantity_available >= quantity]
        zero_price = 0
        stock = sorted(
            stock, key=(lambda s: s.cost_price or zero_price), reverse=False)
        if stock:
            return stock[0]
        return None

    def has_active_sales(self):
        today = date.today()
        return self.sales.filter(active=True).filter(Q(end_date__gte=today) | Q(end_date__isnull=True)).exists()

    def get_active_sales(self):
        today = date.today()
        return self.sales.filter(active=True).filter(Q(end_date__gte=today) | Q(end_date__isnull=True))

    def get_sku(self):
        main_sku = self.product.color_variations.filter(is_main_sku=True).first()
        if main_sku is None:
            main_sku = self.product.color_variations.first()
        if main_sku is not None:
            sku = main_sku.SKU
        else:
            sku = 'No SKU for this product'
        return sku



class StockLocation(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        permissions = (
            ('view_stock_location',
             pgettext_lazy('Permission description',
                           'Can view stock location')),
            ('edit_stock_location',
             pgettext_lazy('Permission description',
                           'Can edit stock location')))

    def __str__(self):
        return self.name


class Stock(models.Model):
    variant = models.ForeignKey(
        ProductVariant, related_name='stock', on_delete=models.CASCADE)
    location = models.ForeignKey(
        StockLocation, null=True, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        validators=[MinValueValidator(0)], default=Decimal(1))
    quantity_allocated = models.IntegerField(
        validators=[MinValueValidator(0)], default=Decimal(0))
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        blank=True, null=True)

    class Meta:
        app_label = 'product'
        unique_together = ('variant', 'location')

    def __str__(self):
        return '%s - %s' % (self.variant.name, self.location)

    @property
    def quantity_available(self):
        return max(self.quantity - self.quantity_allocated, 0)

    def get_total(self):
        if self.cost_price:
            return self.cost_price

