from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from resumos.models import Disciplina, Ano, Resumo

class Command(BaseCommand):
    help = 'Adiciona dados iniciais (disciplinas e anos) ao banco de dados'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('A criar dados...'))

        # Criar disciplinas
        disciplinas = [
            'Matemática',
            'Português',
            'História',
            'Geografia',
            'Ciências Naturais',
            'Física',
            'Química',
            'Biologia',
            'Inglês',
            'Filosofia',
            'Educação Física',
            'Artes',
            'Geometria Descritiva A',
            'Matemática A',
            'Econemia A',
            'EMRC',
            'MACS',
            'História B',
            'APINF',
            'História A',
            'HGP',
            'Física e Química A',
            'Físico-química',
            'História e Cultura das Artes',
            'Francês',
            'Espanhol',
            'Geografia A',
            'Biologia e Geologia',
            'Economia C',
            'Ciência Política',
            'Psicologia',


        ]

        for nome in disciplinas:
            disciplina, created = Disciplina.objects.get_or_create(nome=nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f' Disciplina criada: {nome}'))
            else:
                self.stdout.write(f'- Disciplina já existe: {nome}')

        # Criar anos 
        for numero in range(7, 13):
            ano, created = Ano.objects.get_or_create(numero=numero)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Ano criado: {numero}º Ano'))
            else:
                self.stdout.write(f'- Ano já existe: {numero}º Ano')

        self.stdout.write(self.style.SUCCESS('\n  Dados iniciais criados com sucesso!'))
        self.stdout.write(self.style.WARNING('\n  Não esqueça de criar um superusuário:'))
        self.stdout.write('   python manage.py createsuperuser')
