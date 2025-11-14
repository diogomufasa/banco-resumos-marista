# Gestão de Disciplinas por Ano

## Descrição

O sistema permite configurar quais disciplinas estão disponíveis em cada ano escolar. Isso é útil porque certas disciplinas são específicas de determinados anos:

- **Ciências**: normalmente disponível nos anos 7, 8 e 9
- **Biologia, Física, Química**: normalmente disponíveis nos anos 10, 11 e 12
- **Filosofia, Sociologia**: normalmente disponíveis nos anos 10, 11 e 12
- **Artes**: normalmente disponível nos anos 7, 8 e 9

## Como Funciona

### Comportamento do Sistema

1. **Disciplinas com anos configurados**: Aparecem apenas nos anos especificados
2. **Disciplinas sem anos configurados**: Aparecem em todos os anos (disciplinas gerais)

### Filtragem Dinâmica

- **Na lista de resumos**: Ao selecionar um ano, apenas as disciplinas disponíveis para aquele ano aparecem no filtro
- **Ao criar/editar resumo**: Ao selecionar um ano, apenas as disciplinas disponíveis para aquele ano aparecem no dropdown

## Como Configurar

### Método 1: Via Django Admin (Recomendado)

1. Acesse o painel de administração: `/admin`
2. Vá para **Disciplinas**
3. Clique na disciplina que deseja configurar
4. No campo **Anos Disponíveis**, selecione os anos em que a disciplina está disponível
5. Deixe vazio se a disciplina estiver disponível em todos os anos
6. Clique em **Guardar**

### Método 2: Via Comando de Gestão

Execute o comando para configurar automaticamente as relações padrão:

```bash
cd src
python manage.py setup_disciplinas_anos
```

Este comando configura automaticamente as disciplinas mais comuns com seus anos típicos.

### Método 3: Via Shell do Django

```bash
cd src
python manage.py shell
```

```python
from resumos.models import Disciplina, Ano

# Exemplo: Configurar Biologia apenas para 10º, 11º e 12º anos
biologia = Disciplina.objects.get(nome='Biologia')
anos = Ano.objects.filter(numero__in=[10, 11, 12])
biologia.anos_disponiveis.set(anos)

# Exemplo: Configurar Matemática para todos os anos
matematica = Disciplina.objects.get(nome='Matemática')
todos_anos = Ano.objects.all()
matematica.anos_disponiveis.set(todos_anos)

# Exemplo: Remover restrições (disponível para todos)
disciplina = Disciplina.objects.get(nome='Nome da Disciplina')
disciplina.anos_disponiveis.clear()
```

## Exemplos de Configuração

### Configuração Típica do Ensino Básico (7º-9º ano)

- Matemática
- Português
- História
- Geografia
- Ciências
- Inglês
- Educação Física
- Artes

### Configuração Típica do Ensino Secundário (10º-12º ano)

- Matemática
- Português
- História
- Geografia
- Biologia
- Física
- Química
- Inglês
- Filosofia
- Sociologia
- Educação Física

## Verificar Configuração Atual

Para ver quais disciplinas estão configuradas para cada ano:

```bash
cd src
python manage.py shell
```

```python
from resumos.models import Disciplina, Ano

# Ver todas as disciplinas e seus anos
for disciplina in Disciplina.objects.all():
    anos = disciplina.anos_disponiveis.all()
    if anos:
        print(f"{disciplina.nome}: {', '.join([str(a.numero) for a in anos])}º anos")
    else:
        print(f"{disciplina.nome}: Todos os anos (sem restrição)")

# Ver disciplinas de um ano específico
ano = Ano.objects.get(numero=10)
disciplinas = Disciplina.objects.filter(anos_disponiveis=ano) | Disciplina.objects.filter(anos_disponiveis__isnull=True)
print(f"Disciplinas disponíveis no {ano}:")
for d in disciplinas.distinct():
    print(f"  - {d.nome}")
```

## Notas Importantes

1. **Disciplinas Existentes**: Se já existem resumos criados antes desta funcionalidade, eles continuarão acessíveis normalmente
2. **Flexibilidade**: O sistema permite total flexibilidade na configuração - ajuste conforme as necessidades da sua escola
3. **Manutenção**: Recomenda-se revisar as configurações no início de cada ano letivo
