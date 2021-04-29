from django.urls import path

from . import views

app='tablet'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('qr/', views.qr, name='home'),
]
