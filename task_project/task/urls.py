"""task URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve

from .core import views as core_view
from .promocodes.urls import urlpatterns as promocodes_urls
from .cart.urls import urlpatterns as cart_urls
from .product.urls import urlpatterns as product_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    
    url(r'^$', core_view.main),
    url(r'^', include((cart_urls, 'cart'), namespace='cart')),
    url(r'^', include(promocodes_urls)),
    url(r'^', include((product_urls, 'product'), namespace='product')),

] + [
                       url(r'^static/(?P<path>.*)$', serve)] + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
