from django.urls import path

from . import views

app_name = 'login'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('reset', views.reset, name='reset'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register')
]
