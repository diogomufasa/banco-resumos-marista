from django.core.management.base import BaseCommand
from resumos.models import Disciplina, Ano

class Command(BaseCommand):
    help = 'Configura as relações entre disciplinas e anos'

    def handle(self, *args, **kwargs):
        """
        Este comando ajuda a configurar quais disciplinas estão disponíveis em quais anos.
        Por padrão, se uma disciplina não tiver anos configurados, ela estará disponível para todos os anos.
        """
        
        # Exemplo de configuração - ajuste conforme necessário
        configuracoes = {
            'Matemática': [5, 6, 7, 8, 9],
            'Português': [5, 6, 7, 8, 9, 10, 11, 12],
            'História': [7, 8, 9],
            'Geografia': [7, 8, 9],
            'Ciências Naturais': [5, 6, 7, 8, 9],
            'Biologia': [12],
            'Física': [12],
            'Química': [12],
            'Inglês': [5, 6, 7, 8, 9, 10, 11, 12],
            'Educação Física': [5, 6, 7, 8, 9, 10, 11, 12],
            'Artes': [10, 11, 12],
            'Filosofia': [10, 11, 12],
            'Geometria Descritiva A': [10, 11],
            'Econemia A': [10, 11],
            'EMRC': [5, 6, 7, 8, 9, 10, 11, 12],
            'MACS': [12],
            'Geografia A': [10,11],
            'História B': [10,11],
            'APINF': [12],
            'História A': [10,11,12],
            'HGP': [5,6],
            'Física e Química A': [10,11],
            'Físico-química': [7,8,9],
            'História e Cultura das Artes': [10,11],
            'Francês': [7,8,9],
            'Espanhol': [7,8,9],
            'Psicologia': [12],
            'Ciência Política': [12],
            'Biologia e Geologia': [10,11],
            'Matemática A': [10,11,12],
            'Econemia C': [12],
            


        }
        
        self.stdout.write(self.style.SUCCESS('Configurando relações disciplinas-anos...'))
        
        for disciplina_nome, anos_numeros in configuracoes.items():
            try:
                disciplina = Disciplina.objects.get(nome=disciplina_nome)
                anos = Ano.objects.filter(numero__in=anos_numeros)
                
                # Limpar relações antigas
                disciplina.anos_disponiveis.clear()
                
                # Adicionar novas relações
                disciplina.anos_disponiveis.add(*anos)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f' {disciplina_nome}: configurada para os anos {", ".join(map(str, anos_numeros))}'
                    )
                )
            except Disciplina.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f' Disciplina "{disciplina_nome}" não encontrada. Ignorando.'
                    )
                )
        
        # Contar disciplinas sem anos configurados
        disciplinas_sem_anos = Disciplina.objects.filter(anos_disponiveis__isnull=True).distinct()
        if disciplinas_sem_anos.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\n {disciplinas_sem_anos.count()} disciplina(s) sem anos configurados '
                    f'(estarão disponíveis para todos os anos):'
                )
            )
            for disc in disciplinas_sem_anos:
                self.stdout.write(f'  - {disc.nome}')
        
        self.stdout.write(self.style.SUCCESS('\n Configuração concluída!'))
