from django.core.management.base import BaseCommand
from resumos.models import Tag

class Command(BaseCommand):
    help = 'Configura tags padrão no sistema'

    def handle(self, *args, **kwargs):
        tags_padrão = [
            {'nome': 'Resumo', 'cor': '#28a745'},
            {'nome': 'Testes', 'cor': '#ffc107'},
            {'nome': 'Trabalhos', 'cor': '#17a2b8'},
            {'nome': 'Exercícios com resolução', 'cor': '#6f42c1'},
            {'nome': 'Exercícios sem resolução', 'cor': '#0066cc'},
            {'nome': 'Exames', 'cor': '#fd7e14'},

        ]
        
        self.stdout.write(self.style.SUCCESS('Configurando tags padrão...'))
        
        for tag_data in tags_padrão:
            tag, created = Tag.objects.get_or_create(
                nome=tag_data['nome'],
                defaults={'cor': tag_data['cor']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f' Tag "{tag.nome}" criada com cor {tag.cor}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f' Tag "{tag.nome}" já existe')
                )
        
        self.stdout.write(self.style.SUCCESS('\n Configuração concluída!'))
