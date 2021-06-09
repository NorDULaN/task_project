# Generated by Django 2.0.13 on 2021-06-02 08:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_auto_20210602_1540'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'permissions': (('view_category', 'Can view categories'), ('edit_category', 'Can edit categories'), ('view_sku_global', 'Can view SKU'), ('edit_sku_global', 'Can edit SKU'))},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'permissions': (('view_product', 'Can view products'), ('edit_product', 'Can edit products'), ('view_properties', 'Can view product properties'), ('edit_properties', 'Can edit product properties'), ('brandquad_attr', 'Can access to Brandquad attributes'), ('banner_edit', 'Can edit product banners'), ('equipments_edit', 'Can edit product equipments'), ('tech_spec_edit', 'Can edit product tech specifications'), ('alt_cat_edit', 'Can edit product alt category'), ('files_edit', 'Can edit product files'), ('photo_add', 'Can add product photo'), ('photo_remove', 'Can remove product photo'), ('photo_change', 'Can change photo data on product')), 'verbose_name': 'Product template'},
        ),
    ]