from django.contrib import admin
from .models import Disciplina, Ano, Resumo, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor']
    search_fields = ['nome']
    
@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'get_anos_disponiveis']
    search_fields = ['nome']
    filter_horizontal = ['anos_disponiveis']
    
    def get_anos_disponiveis(self, obj):
        anos = obj.anos_disponiveis.all()
        if anos:
            return ', '.join([f"{ano.numero}º" for ano in anos])
        return "Todos os anos"
    get_anos_disponiveis.short_description = 'Anos Disponíveis'

@admin.register(Ano)
class AnoAdmin(admin.ModelAdmin):
    list_display = ['numero']
    ordering = ['numero']

@admin.register(Resumo)
class ResumoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'disciplina', 'ano', 'autor', 'data_criacao']
    list_filter = ['disciplina', 'ano', 'data_criacao', 'tags']
    search_fields = ['titulo', 'conteudo', 'autor__username']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    date_hierarchy = 'data_criacao'
    filter_horizontal = ['tags']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se for novo objeto
            obj.autor = request.user
        super().save_model(request, obj, form, change)