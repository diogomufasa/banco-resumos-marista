# 📚 Banco de Resumos para o Colégio Marista

## 🚀 Quickstart

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Aplicar Migrações da Base de Dados

```bash
cd src
python manage.py migrate
```

### 3. Criar Dados Iniciais (Disciplinas, Anos e Tags)

```bash
python manage.py setup_initial_data
python manage.py setup_disciplinas_anos
python manage.py setup_tags
```

### 4. Criar Admin User

```bash
python manage.py createsuperuser
```

Preencha:
- Username (nome de usuário)
- Email (opcional)
- Password (senha)

### 5. Executar o Servidor

```bash
python manage.py runserver
```

### 6. Acessar a Aplicação

- **Site principal**: http://127.0.0.1:8000/
- **Admin (gestão)**: http://127.0.0.1:8000/admin/

---

## 🎯 Funcionalidades

### 📝 Para Utilizadores
- ✅ **Pesquisa Avançada**: Barra de pesquisa no header para buscar resumos por título, conteúdo ou tags
- ✅ **Filtros**: Filtrar resumos por ano e disciplina
- ✅ **Registo de Conta**: Criar conta própria sem precisar do admin
- ✅ **Ver Resumos**: Acesso a todos os resumos partilhados
- ✅ **Upload de Ficheiros**: Anexar PDFs e outros documentos aos resumos

### 👤 Para Autores (Utilizadores Autenticados)
- ✅ **Criar Resumos**: Adicionar novos resumos com título, conteúdo e tags
- ✅ **Editar Resumos**: Modificar os próprios resumos
- ✅ **Apagar Resumos**: Remover os próprios resumos
- ✅ **Exportar PDF**: Gerar PDF dos resumos

### 👨‍💼 Para Administradores
- ✅ **Gestão Completa**: Acesso ao painel admin do Django
- ✅ **Gerir Utilizadores**: Criar, editar e remover utilizadores
- ✅ **Gerir Disciplinas**: Adicionar e configurar disciplinas
- ✅ **Gerir Anos**: Adicionar anos escolares
- ✅ **Gerir Tags**: Criar tags personalizadas com cores

---

## 🎨 Design e Interface

- 🎨 **Paleta de Cores Moderna**: Interface com tons de azul profissional
- 📱 **Design Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- 🔍 **Pesquisa Integrada**: Barra de pesquisa sempre acessível no header
- 💫 **Animações Suaves**: Efeitos hover e transições elegantes
- 🃏 **Cards Modernos**: Layout em cards com bordas arredondadas

---

## 🎯 Configuração Inicial (Detalhada)

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Aplicar Migrações da Base de Dados

```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

### 3. Criar Dados Iniciais

```bash
# Criar disciplinas e anos
python manage.py setup_initial_data

# Configurar relação disciplinas-anos
python manage.py setup_disciplinas_anos

# Criar tags padrão
python manage.py setup_tags
```

### 4. Criar Admin User

```bash
python manage.py createsuperuser
```

Preencha:
- Username (nome de usuário)
- Email (opcional)
- Password (senha)

### 5. Executar o Servidor

```bash
python manage.py runserver
```

### 6. Acessar a Aplicação

- **Site principal**: http://127.0.0.1:8000/
- **Admin (gestão)**: http://127.0.0.1:8000/admin/


## 📁 Estrutura do Projeto

```
src/
├── banco_resumos_django/    # Configurações do projeto
│   ├── settings.py         # Configurações gerais
│   ├── urls.py            # URLs principais
│   └── wsgi.py
├── resumos/                # App principal
│   ├── models.py          # Modelos (Disciplina, Ano, Resumo, Tag)
│   ├── views.py           # Lógica das páginas
│   ├── urls.py            # URLs da app
│   ├── admin.py           # Configuração do admin
│   ├── management/        # Comandos personalizados
│   │   └── commands/
│   │       ├── setup_initial_data.py
│   │       ├── setup_disciplinas_anos.py
│   │       └── setup_tags.py
│   ├── templates/         # Templates HTML
│   │   └── resumos/
│   │       ├── base.html
│   │       ├── lista.html
│   │       ├── detalhe.html
│   │       ├── form.html
│   │       ├── login.html
│   │       ├── signup.html
│   │       ├── perfil.html
│   │       └── confirmar_delete.html
│   └── static/            # CSS, JS, imagens
│       └── resumos/
│           └── css/
│               └── style.css
├── media/                 # Uploads de arquivos
└── manage.py             # Script de gestão Django
```

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.2
- **Frontend**: HTML5, Bootstrap 5, CSS3, JavaScript
- **Base de Dados**: SQLite (desenvolvimento)
- **Bibliotecas**: ReportLab (geração de PDF)
- **Python**: 3.x

## 🎨 Personalização

### Adicionar Novas Tags

Via Admin:
1. Acesse http://127.0.0.1:8000/admin/
2. Vá para "Tags"
3. Clique em "Adicionar Tag"
4. Digite o nome e escolha uma cor (formato hex: #RRGGBB)

Via Comando:
```bash
python manage.py shell
```
```python
from resumos.models import Tag
Tag.objects.create(nome='Minha Tag', cor='#ff5733')
```

### Configurar Disciplinas por Ano

Consulte o arquivo `DISCIPLINAS_ANOS.md` para instruções detalhadas sobre como configurar quais disciplinas estão disponíveis em cada ano.

---

## 📝 Comandos Úteis

### Criar nova app Django
```bash
python manage.py startapp nome_da_app
```

### Criar novas migrações após alterar models.py
```bash
python manage.py makemigrations
python manage.py migrate
```

### Abrir shell Django (testar código)
```bash
python manage.py shell
```

### Criar mais utilizadores
- **Via Signup**: Acesse http://127.0.0.1:8000/signup/
- **Via Admin**: http://127.0.0.1:8000/admin/ → "Users" → "Adicionar"

### Reinicializar Base de Dados
```bash
cd src
rm db.sqlite3
python manage.py migrate
python manage.py setup_initial_data
python manage.py setup_disciplinas_anos
python manage.py setup_tags
python manage.py createsuperuser
```

## 🐛 Resolução de Problemas

### Erro: "No module named 'resumos'"
- Certifique-se que está na pasta `src/`
- Verifique se `resumos` está em `INSTALLED_APPS` no `settings.py`

### Erro: "Table doesn't exist"
```bash
python manage.py migrate
```

### Página de login não funciona
- Certifique-se que criou um superusuário ou uma conta via signup
- Verifique se o URL `/login/` está configurado

### CSS não aparece
```bash
python manage.py collectstatic
```

### Servidor não inicia
- Verifique se a porta 8000 está livre
- Tente usar outra porta: `python manage.py runserver 8080`

---

## 🎯 Recursos e Funcionalidades Técnicas

### Backend (Django)
- ✅ Sistema de autenticação completo
- ✅ Signup de utilizadores
- ✅ Upload de ficheiros
- ✅ Exportação para PDF (ReportLab)
- ✅ Filtros avançados (Q objects)
- ✅ RelacionamentosMany-to-Many (Tags)
- ✅ Management commands personalizados

### Frontend
- ✅ Bootstrap 5 responsivo
- ✅ CSS customizado com variáveis
- ✅ JavaScript para filtros dinâmicos
- ✅ Validação de formulários
- ✅ Animações e transições suaves
- ✅ Ícones SVG integrados

### Base de Dados
- ✅ SQLite (desenvolvimento)
- ✅ Migrações automáticas
- ✅ Seeding de dados inicial
- ✅ Relações complexas entre modelos

---

## 📊 Estatísticas do Projeto

**Modelos Django**: 4 (Disciplina, Ano, Resumo, Tag)
**Views**: 10+ views funcionais
**Templates**: 8 páginas HTML
**Management Commands**: 3 comandos personalizados
**Disciplinas Pré-configuradas**: 30+
**Anos Escolares**: 6 (7º ao 12º)
**Tags Padrão**: 6 tags

---

**© 2024 Banco de Resumos Marista - Projeto Escolar**
