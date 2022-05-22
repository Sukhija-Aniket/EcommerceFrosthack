from . import views
from django.urls import path

app_ame = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('checkout/', views.checkout, name="checkout"),
    path('product/<slug>/',views.ItemDetailView.as_view(),name='product'),
    path('add-to-cart/<slug>/',views.add_to_cart,name='add-to-cart'),
    path('remove-from-cart/<slug>/',views.remove_from_cart,name='remove-from-cart'),
]
