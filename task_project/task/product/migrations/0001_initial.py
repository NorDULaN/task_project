# Generated by Django 2.0.13 on 2021-06-01 08:54

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_default', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=128)),
                ('h1', models.CharField(blank=True, max_length=128)),
                ('slug', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
                ('seo_title', models.CharField(blank=True, max_length=255)),
                ('seo_desc', models.CharField(blank=True, max_length=1000)),
                ('seo_keys', models.CharField(blank=True, max_length=255)),
                ('id_item', models.IntegerField(null=True)),
                ('priority', models.IntegerField(blank=True, default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('product_relations_title_localize', models.CharField(default='__product_relations__', max_length=255)),
                ('installation', models.BooleanField(default=False)),
                ('filter_registration', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='product.Category')),
            ],
            options={
                'permissions': (('view_category', 'Can view categories'), ('edit_category', 'Can edit categories'), ('view_sku_global', 'Can view SKU'), ('edit_sku_global', 'Can edit SKU')),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('is_published', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('promo_cover', models.FileField(blank=True, null=True, upload_to='')),
                ('ean_code', models.CharField(blank=True, default='', max_length=255)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='product.Category')),
            ],
            options={
                'permissions': (('view_product', 'Can view products'), ('edit_product', 'Can edit products'), ('view_properties', 'Can view product properties'), ('edit_properties', 'Can edit product properties'), ('brandquad_attr', 'Can access to Brandquad attributes'), ('banner_edit', 'Can edit product banners'), ('equipments_edit', 'Can edit product equipments'), ('tech_spec_edit', 'Can edit product tech specifications'), ('alt_cat_edit', 'Can edit product alt category'), ('files_edit', 'Can edit product files'), ('photo_add', 'Can add product photo'), ('photo_remove', 'Can remove product photo'), ('photo_change', 'Can change photo data on product')),
            },
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('has_variants', models.BooleanField(default=True)),
                ('is_shipping_required', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('path', models.TextField()),
                ('is_active', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, default='')),
                ('short_description', models.TextField(blank=True, default='', max_length=256)),
                ('teaser_desc', models.TextField(blank=True, default='')),
                ('attr_show', models.BooleanField(default=True)),
                ('add_default', models.BooleanField(default=False)),
                ('seo_title', models.CharField(blank=True, max_length=2000)),
                ('seo_description', models.CharField(blank=True, max_length=2000, null=True, validators=[django.core.validators.MaxLengthValidator(2000)])),
                ('seo_keywords', models.CharField(blank=True, max_length=100)),
                ('priority', models.IntegerField(blank=True, default=1000)),
                ('use_alt_category', models.BooleanField(default=False)),
                ('price_override', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('show_in_discounts', models.BooleanField(default=False)),
                ('registration_block', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(blank=True, default=0, help_text='Product with the highest number will be the first in the list')),
                ('alt_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.Category')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='product.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=Decimal('1'), validators=[django.core.validators.MinValueValidator(0)])),
                ('quantity_allocated', models.IntegerField(default=Decimal('0'), validators=[django.core.validators.MinValueValidator(0)])),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'permissions': (('view_stock_location', 'Can view stock location'), ('edit_stock_location', 'Can edit stock location')),
            },
        ),
        migrations.AddField(
            model_name='stock',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.StockLocation'),
        ),
        migrations.AddField(
            model_name='stock',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock', to='product.ProductVariant'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='product.ProductType'),
        ),
        migrations.AlterUniqueTogether(
            name='stock',
            unique_together={('variant', 'location')},
        ),
    ]
