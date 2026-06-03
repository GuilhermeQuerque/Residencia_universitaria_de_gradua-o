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
from .impressao import ErroImpressao, contar_paginas, imprimir_arquivo
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
            arquivos = form.cleaned_data['arquivo']
            descricao = form.cleaned_data['descricao']
            total_paginas = 0
            arquivos_processados = []
            erros = []

            for arquivo in arquivos:
                nome = arquivo.name
                sufixo = Path(nome).suffix or '.bin'
                caminho = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
                        for pedaco in arquivo.chunks():
                            tmp.write(pedaco)
                        caminho = Path(tmp.name)

                    pag = contar_paginas(caminho)
                    imprimir_arquivo(caminho)

                    total_paginas += pag
                    arquivos_processados.append(nome)
                except ErroImpressao as e:
                    erros.append(f'{nome}: {e}')
                finally:
                    if caminho and caminho.exists():
                        os.unlink(caminho)

            if arquivos_processados:
                nomes_str = ', '.join(arquivos_processados)
                descricao_log = f'Arquivos: {nomes_str}. {descricao}'.strip().rstrip('.')
                LogImpressao.objects.create(
                    usuario=request.user,
                    paginas=total_paginas,
                    status='ok',
                    descricao=descricao_log,
                )
                Pagamento.objects.create(
                    usuario=request.user,
                    valor=preco_por_pagina * total_paginas,
                    observacao=(
                        f'Cobranca automatica: {total_paginas} pagina(s) - '
                        f'arquivos: {nomes_str}.'
                    ),
                )
                qtd = len(arquivos_processados)
                msg = f'{qtd} arquivo(s) enviado(s) para a impressora "{settings.IMPRESSORA_NOME}".'
                messages.success(request, msg)

            if erros:
                for e in erros:
                    messages.error(request, f'Erro ao imprimir: {e}')
                LogImpressao.objects.create(
                    usuario=request.user,
                    paginas=0,
                    status='erro',
                    descricao=f'Erro(s): {"; ".join(erros)}. {descricao}',
                )

            if arquivos_processados:
                return redirect('dashboard')
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
