from django.db import models
from django.contrib.auth.models import User

class Ano(models.Model):
    numero = models.IntegerField(unique=True)  # 7, 8, 9, 10, 11, 12
    
    def __str__(self):
        return f"{self.numero}º Ano"
    
    class Meta:
        verbose_name_plural = "Anos"
        ordering = ['numero']

class Disciplina(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    anos_disponiveis = models.ManyToManyField(Ano, related_name='disciplinas', blank=True)
    
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
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='resumos')
    ano = models.ForeignKey(Ano, on_delete=models.CASCADE, related_name='resumos')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumos')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    arquivo = models.FileField(upload_to='resumos/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='resumos', blank=True)
    
    def __str__(self):
        return f"{self.titulo} - {self.disciplina.nome}"
    
    class Meta:
        verbose_name_plural = "Resumos"
        ordering = ['-data_criacao']