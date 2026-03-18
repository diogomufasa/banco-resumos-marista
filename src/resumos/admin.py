from django.contrib import admin
from .models import Disciplina, Ano, Resumo, Tag, VerificationSettings


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
    list_display = ['titulo', 'disciplina', 'ano',
                    'autor', 'is_approved', 'data_criacao']
    list_filter = ['disciplina', 'ano', 'is_approved', 'data_criacao', 'tags']
    search_fields = ['titulo', 'conteudo', 'autor__username']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    date_hierarchy = 'data_criacao'
    filter_horizontal = ['tags']
    actions = ['marcar_como_aprovado', 'marcar_como_pendente']

    def save_model(self, request, obj, form, change):
        if not change:  # Se for novo objeto
            obj.autor = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description='Marcar resumos selecionados como aprovados')
    def marcar_como_aprovado(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Marcar resumos selecionados como pendentes')
    def marcar_como_pendente(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(VerificationSettings)
class VerificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['admin_email']

    def has_add_permission(self, request):
        # Permitir apenas um registo de configuração
        if VerificationSettings.objects.count() >= 1:
            return False
        return super().has_add_permission(request)
