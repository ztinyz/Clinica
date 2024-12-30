from django.urls import path
from . import views

app_name = 'login'
urlpatterns = [
    path('', views.dash_view, name='dash'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email')
]
