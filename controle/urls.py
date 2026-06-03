from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    LoginSimplesView,
    LogoutSimplesView,
    dashboard,
    registrar,
    solicitar_impressao,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', LoginSimplesView.as_view(), name='login'),
    path('logout/', LogoutSimplesView.as_view(), name='logout'),
    path('registrar/', registrar, name='registrar'),
    path('impressao/solicitar/', solicitar_impressao, name='solicitar_impressao'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
