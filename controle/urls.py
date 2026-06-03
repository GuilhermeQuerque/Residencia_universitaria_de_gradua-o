from django.urls import path

from .views import (
    LoginSimplesView,
    LogoutSimplesView,
    dashboard,
    solicitar_impressao,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', LoginSimplesView.as_view(), name='login'),
    path('logout/', LogoutSimplesView.as_view(), name='logout'),
    path('impressao/solicitar/', solicitar_impressao, name='solicitar_impressao'),
]
