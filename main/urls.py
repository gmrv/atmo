from django.urls import path

from . import views

app='main'
urlpatterns = [
    path('', views.index, name='index'),

    path('area_select/', views.area_select, name='area_select'),

    path('home/', views.home, name='home'),
    path('home/<int:area_id>', views.home, name='home'),
    path('home/<int:area_id>/<slug:target_date>', views.home, name='home'),
    path('home/<slug:target_date>', views.home, name='home'),

    path('cells/<int:area_id>', views.cells, name='cells'),
    path('cells/<int:area_id>/<slug:target_date>', views.cells, name='cells'),

    path('resource/<int:resource_id>', views.resource, name='resource'),
    path('resource/<int:resource_id>/<slug:target_date>', views.resource, name='resource'),

    path('profile/', views.profile, name='profile'),
    path('profile/<slug:target_date>', views.profile, name='profile'),
]
