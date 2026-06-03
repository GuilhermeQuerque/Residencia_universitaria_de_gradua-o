from django.contrib import admin
from .models import ImpressoraConfig, LogImpressao, Pagamento, Perfil


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'data_pagamento')
    search_fields = ('usuario__username',)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cpf', 'inscricao')
    search_fields = ('usuario__username',)


@admin.register(LogImpressao)
class LogImpressaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'paginas', 'status', 'criado_em')
    list_filter = ('status',)
    search_fields = ('usuario__username',)


@admin.register(ImpressoraConfig)
class ImpressoraConfigAdmin(admin.ModelAdmin):
    list_display = ('nome',)
