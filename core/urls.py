from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from . import views
from django.urls import path, include

app_ame = 'core'

urlpatterns = [
    path('', views.item_list, name="item-list"),
    path('product-list/', views.product_list, name="product-list")
]
