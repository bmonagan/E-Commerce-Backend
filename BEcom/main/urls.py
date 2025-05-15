from django.urls import include,path
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.conf.urls.static import static
from django.conf import settings



from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('shop/', views.shop, name='shop'),
    path('cart/', include('cart.urls', namespace='cart')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)