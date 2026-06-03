import os
import tempfile
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from .forms import RegistroForm, SolicitarImpressaoForm
from .impressao import ErroImpressao, imprimir_arquivo
from .models import LogImpressao, Pagamento, Perfil


class LoginSimplesView(LoginView):
    template_name = 'controle/login.html'


class LogoutSimplesView(LogoutView):
    template_name = 'controle/logout.html'
    next_page = 'login'
    http_method_names = ["get", "post", "options"]

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data())


@login_required
def dashboard(request):
    pagamentos = Pagamento.objects.filter(usuario=request.user).order_by('-data_pagamento')[:5]
    logs = LogImpressao.objects.filter(usuario=request.user).order_by('-criado_em')[:5]
    return render(
        request,
        'controle/dashboard.html',
        {
            'pagamentos': pagamentos,
            'logs': logs,
        },
    )


@login_required
def solicitar_impressao(request):
    preco_por_pagina = Decimal('0.50')

    if request.method == 'POST':
        form = SolicitarImpressaoForm(request.POST, request.FILES)
        if form.is_valid():
            paginas = form.cleaned_data['paginas']
            arquivo = form.cleaned_data['arquivo']
            descricao = form.cleaned_data['descricao']
            nome_arquivo = arquivo.name
            descricao_log = f'Arquivo: {nome_arquivo}. {descricao}'.strip()
            sufixo = Path(nome_arquivo).suffix or '.bin'
            caminho_temp = None

            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
                    for pedaco in arquivo.chunks():
                        tmp.write(pedaco)
                    caminho_temp = Path(tmp.name)

                imprimir_arquivo(caminho_temp)

                LogImpressao.objects.create(
                    usuario=request.user,
                    paginas=paginas,
                    status='ok',
                    descricao=descricao_log,
                )
                Pagamento.objects.create(
                    usuario=request.user,
                    valor=preco_por_pagina * paginas,
                    observacao=(
                        f'Cobranca automatica: {paginas} pagina(s) - arquivo {nome_arquivo}.'
                    ),
                )
                messages.success(
                    request,
                    f'Arquivo enviado para a impressora "{settings.IMPRESSORA_NOME}".',
                )
                return redirect('dashboard')
            except ErroImpressao as erro:
                LogImpressao.objects.create(
                    usuario=request.user,
                    paginas=paginas,
                    status='erro',
                    descricao=f'{descricao_log} Erro: {erro}',
                )
                messages.error(request, str(erro))
            finally:
                if caminho_temp and caminho_temp.exists():
                    os.unlink(caminho_temp)
    else:
        form = SolicitarImpressaoForm()

    return render(
        request,
        'controle/solicitar_impressao.html',
        {
            'form': form,
            'preco_por_pagina': preco_por_pagina,
            'impressora_nome': settings.IMPRESSORA_NOME or '(nao configurada)',
        },
    )


def registrar(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            nome = form.cleaned_data['nome'].strip()
            senha = form.cleaned_data['senha']
            cpf = form.cleaned_data.get('cpf') or None
            inscricao = form.cleaned_data.get('inscricao') or None

            username_base = email.split('@')[0][:30]
            username = username_base
            contador = 1
            while User.objects.filter(username=username).exists():
                username = f'{username_base}{contador}'
                contador += 1

            partes_nome = nome.split(' ', 1)
            primeiro_nome = partes_nome[0]
            sobrenome = partes_nome[1] if len(partes_nome) > 1 else ''

            user = User.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=primeiro_nome,
                last_name=sobrenome,
            )
            Perfil.objects.create(
                usuario=user,
                cpf=make_password(cpf) if cpf else None,
                inscricao=make_password(str(inscricao)) if inscricao else None,
            )
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = RegistroForm()

    return render(request, 'controle/registrar.html', {'form': form})
