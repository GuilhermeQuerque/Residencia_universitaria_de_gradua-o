from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cpf = models.CharField(max_length=11, blank=True, null=True, verbose_name='CPF')
    inscricao = models.CharField(max_length=50, blank=True, null=True, verbose_name='Inscricao')

    def __str__(self):
        return f'{self.usuario.username} - Perfil'


class Pagamento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    data_pagamento = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.usuario.username} - R$ {self.valor}'


class LogImpressao(models.Model):
    STATUS_CHOICES = [
        ('ok', 'Ok'),
        ('pendente', 'Pendente'),
        ('erro', 'Erro'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    paginas = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ok')
    criado_em = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.paginas} pagina(s) - {self.status}'


class ImpressoraConfig(models.Model):
    nome = models.CharField(max_length=100, blank=True, verbose_name='Nome da fila CUPS')

    def __str__(self):
        return self.nome or '(nenhuma)'
