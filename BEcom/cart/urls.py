from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('product_list', views.product_list, name='product_list'),
    path('home', views.home, name='home'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('clear_cart/', views.clear_user_cart_session, name='clear_cart'),
    path('order_history/', views.order_history, name='order_history'),
]