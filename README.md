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

- Username
- Email (opcional)
- Password

### 5. Executar o Servidor

```bash
python manage.py runserver
```

### 6. Aceder à Aplicação

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
- **Base de Dados**: SQLite
- **Bibliotecas**: ReportLab
- **Python**: 3.x


**© 2024 Banco de Resumos Marista - Projeto Escolar**

