from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
import views as root_views

app_name = 'atmo'
urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),

    # path('', RedirectView.as_view(url='/main/home', permanent=True)),
    path('', root_views.root, name='root'),
    path('main/', include(('main.urls', 'main'), namespace='main')),
    path('api/', include(('api.urls', 'api'), namespace='api'))
]

urlpatterns += [
    path('staff/', include('staff.urls', namespace='staff')),
]