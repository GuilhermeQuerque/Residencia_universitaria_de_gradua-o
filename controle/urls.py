from django.urls import path

from .views import (
    LoginSimplesView,
    LogoutSimplesView,
    dashboard,
    recuperar_senha,
    redefinir_senha,
    registrar,
    selecionar_impressora,
    solicitar_impressao,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', LoginSimplesView.as_view(), name='login'),
    path('logout/', LogoutSimplesView.as_view(), name='logout'),
    path('registrar/', registrar, name='registrar'),
    path('impressao/solicitar/', solicitar_impressao, name='solicitar_impressao'),
    path('recuperar/', recuperar_senha, name='recuperar_senha'),
    path('recuperar/confirmar/', redefinir_senha, name='redefinir_senha'),
    path('impressoras/', selecionar_impressora, name='selecionar_impressora'),
]
