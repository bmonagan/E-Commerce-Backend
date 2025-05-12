from django.urls import path
from django.urls import include,path
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', views.about, name='about'),

    ]