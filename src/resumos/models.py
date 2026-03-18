from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Ano(models.Model):
    numero = models.IntegerField(unique=True)  # 7, 8, 9, 10, 11, 12

    def __str__(self):
        return f"{self.numero}º Ano"

    class Meta:
        verbose_name_plural = "Anos"
        ordering = ['numero']


class Disciplina(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    anos_disponiveis = models.ManyToManyField(
        Ano, related_name='disciplinas', blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Disciplinas"


class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    cor = models.CharField(max_length=7, default='#6c757d')  # Cor hex

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Tags"
        ordering = ['nome']


class Resumo(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, related_name='resumos')
    ano = models.ForeignKey(
        Ano, on_delete=models.CASCADE, related_name='resumos')
    autor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='resumos')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ficheiro = models.FileField(upload_to='resumos/')
    tags = models.ManyToManyField(Tag, related_name='resumos', blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titulo} - {self.disciplina.nome}"

    class Meta:
        verbose_name_plural = "Resumos"
        ordering = ['-data_criacao']


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification_tokens'
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Token de verificação para {self.user.username}"

    def is_valid(self) -> bool:
        if self.used_at is not None:
            return False
        return self.created_at >= timezone.now() - timedelta(days=2)

    class Meta:
        verbose_name = "Token de Verificação de Email"
        verbose_name_plural = "Tokens de Verificação de Email"


class VerificationSettings(models.Model):
    admin_email = models.EmailField(
        'Email para notificações de verificação',
        blank=True,
        help_text=(
            'Endereço que irá receber notificações quando novos utilizadores '
            'ou resumos precisarem de aprovação.'
        ),
    )

    def __str__(self):
        return 'Configurações de Verificação'

    class Meta:
        verbose_name = 'Configuração de Verificação'
        verbose_name_plural = 'Configurações de Verificação'
