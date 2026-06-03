from django.db import models
from django.contrib.auth.models import User


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
