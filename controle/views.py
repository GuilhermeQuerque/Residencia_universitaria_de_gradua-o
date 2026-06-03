import os
import tempfile
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from .forms import SolicitarImpressaoForm
from .impressao import ErroImpressao, imprimir_arquivo
from .models import LogImpressao, Pagamento


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
