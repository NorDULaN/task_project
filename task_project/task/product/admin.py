from django.contrib import admin

from .models import Product, ProductVariant, Category

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductVariant)

from django.contrib.auth.models import Group
admin.site.unregister(Group)