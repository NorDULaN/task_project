from django.db import models
from django.utils import timezone

from task.account.models import User


class Promocode(models.Model):
    TYPE_PERCENT = 0
    TYPE_ABSOLUTE = 1
    TYPE_FREE_SHIPPING = 2
    TYPE_ABSOLUTE_FOR_EACH = 3
    TYPES = (
        (TYPE_PERCENT, 'Percent'),
        (TYPE_ABSOLUTE, 'Absolute'),
        (TYPE_ABSOLUTE_FOR_EACH, 'Absolute'),
        (TYPE_FREE_SHIPPING, 'Free shipping')
    )
    admin_name = models.CharField(blank=True, default='', max_length=255)
    type = models.PositiveSmallIntegerField(default=TYPE_PERCENT, choices=TYPES)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=12, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    code_variants = models.TextField(default='', blank=True,
                                     help_text='Split words by comma. Example: Test, TEST, test')
    products = models.ManyToManyField('product.ProductVariant', blank=True, related_name='promocodes')
    categories = models.ManyToManyField('product.Category', blank=True, related_name='promocodes')
    users = models.ManyToManyField(User, blank=True, related_name='promocodes')
    usage_count = models.PositiveIntegerField(default=0, blank=True)
    min_order_sum = models.DecimalField(default=0, blank=True, decimal_places=2, max_digits=12)
    exclude_active_sales_products = models.BooleanField(default=False)
    exclude_show_in_discounts_products = models.BooleanField(default=False)
    from_base_price = models.BooleanField(default=False)
    products_for_exclude = models.ManyToManyField('product.ProductVariant', blank=True,
                                                  related_name='exclude_promocodes')
    categories_for_exclude = models.ManyToManyField('product.Category', blank=True, related_name='exclude_promocodes')

    def __str__(self):
        return self.code_variants

    def get_main_code_variant(self):
        return self.code_variants.split(',')[0]

    def get_usages(self):
        return self.usages.order_by('-created')

    def get_all_variants_ids(self):

        from ..product.models import ProductVariant, Category

        all_products_ids = set(ProductVariant.objects.values_list('pk', flat=True))
        all_categories_products_ids = set(
            ProductVariant.objects.filter(
                product__category_id__in=list(
                    Category.objects.values_list('id_item', flat=True)
                ),
            ).values_list('pk', flat=True)
        )
        all_ids = all_products_ids.union(all_categories_products_ids)

        if self.products.count() > 0:
            allow_products_ids = set(self.products.values_list('pk', flat=True))
        else:
            allow_products_ids = set()
        if self.categories.count() > 0:
            allow_categories_products_ids = set(
                ProductVariant.objects.filter(
                    product__category_id__in=list(self.categories.values_list('id_item', flat=True)),
                ).values_list('pk', flat=True)
            )
        else:
            allow_categories_products_ids = set()
        all_allow_ids = allow_products_ids.union(allow_categories_products_ids)

        if self.products_for_exclude.count() > 0:
            exclude_product_ids = set(self.products_for_exclude.values_list('pk', flat=True))
        else:
            exclude_product_ids = set()
        if self.categories_for_exclude.count() > 0:
            exclude_categories_products_ids = set(
                ProductVariant.objects.filter(
                    product__category_id__in=list(
                        self.categories_for_exclude.values_list('id_item', flat=True)
                    ),
                ).values_list('pk', flat=True)
            )
        else:
            exclude_categories_products_ids = set()
        all_exclude_ids = exclude_product_ids.union(exclude_categories_products_ids)

        if len(all_allow_ids) > 0 and len(all_exclude_ids) == 0:
            ids = all_allow_ids
        elif len(all_allow_ids) > 0 and len(all_exclude_ids) > 0:
            if len(all_allow_ids) < len(all_exclude_ids):
                ids = all_allow_ids.intersection(all_exclude_ids)
            else:
                ids = all_allow_ids - all_exclude_ids
        elif len(all_allow_ids) == 0 and len(all_exclude_ids) > 0:
            ids = all_ids - all_exclude_ids
        else:
            ids = all_ids

        products_qs = ProductVariant.objects.filter(pk__in=ids)

        if self.exclude_show_in_discounts_products:
            products_qs = products_qs.exclude(show_in_discounts=True)

        if self.exclude_active_sales_products:
            exclude_active_sales_products_ids = []
            for product in products_qs:
                if product.has_active_sales():
                    exclude_active_sales_products_ids.append(product.pk)
            if len(exclude_active_sales_products_ids) > 0:
                products_qs = products_qs.exclude(pk__in=exclude_active_sales_products_ids)

        return set(products_qs.values_list('pk', flat=True))

    def get_saved_money(self, variant, total, rest):

        saved = 0

        products_ids = self.get_all_variants_ids()

        if variant.pk not in products_ids:
            return saved, rest

        if self.type == self.TYPE_PERCENT:
            saved = self.amount / 100 * total

        elif self.type == self.TYPE_ABSOLUTE:

            if rest < total:
                saved = rest
                rest = 0
            else:
                saved = total
                rest -= total

        return saved, rest

    def is_valid(self, user, order_sum, variants_ids):

        now = timezone.now()

        if self.start_date and now < self.start_date:
            return False, '__promocode__error__invalid_date_range__'

        if self.end_date and now > self.end_date:
            return False, '__promocode__error__invalid_date_range__'

        if self.users.count() > 0 and not self.users.filter(pk=user.pk).exists():
            return False, '__promocode__error__invalid_user__'

        if 0 < self.usage_count <= self.get_usages().count():
            return False, '__promocode__error__invalid_usage_count__'

        if self.min_order_sum > 0 and order_sum < self.min_order_sum:
            return False, '__promocode__error__min_order_sum__'

        products_ids = self.get_all_variants_ids()
        if not variants_ids & products_ids:
            return False, '__promocode__error__no_products_for_promocode__'

        return True, '__promocode__msg__success__'


class PromocodeUsage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    promocode = models.ForeignKey(Promocode, related_name='usages', on_delete=models.CASCADE)
    order = models.ForeignKey('order.Order', related_name='promocode_usages', on_delete=models.CASCADE)
