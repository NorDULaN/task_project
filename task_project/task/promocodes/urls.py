from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^promocodes/add_promocode/$', views.add_promocode_to_cart, name="add_promocode_to_cart"),
   url(r'^promocodes/remove_promocode/$', views.remove_promocode, name="remove_promocode"),
]
