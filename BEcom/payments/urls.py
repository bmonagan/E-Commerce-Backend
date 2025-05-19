

from django.urls import path
from . import views
app_name = 'payments'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),
    path('success/', views.SuccessView, name='success'),
    path('cancelled/', views.CancelledView, name='cancelled'),
    path('webhook/', views.stripe_webhook)
]