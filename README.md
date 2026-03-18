# 📚 Banco de Resumos para o Colégio Marista de Carcavelos

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

## 🗄️ Configurar a BD num novo ambiente

Quando clonares o projeto numa máquina/servidor novo, segue estes passos:

1. **Instalar dependências**

	```bash
	pip install -r requirements.txt
	```

2. **Criar e configurar o ficheiro `.env` (na raiz do repo)**

	```bash
	cp .env.example .env
	```

	Depois edita `.env` e preenche, pelo menos:

	- `SECRET_KEY` (podes gerar um novo para produção)
	- `GROQ_API_KEY` (opcional, mas necessário para verificação por AI)
	- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` (para envio de emails de verificação/notificação)

3. **Aplicar migrações** (cria todas as tabelas, incluindo aprovação de resumos e tokens de email)

	```bash
	cd src
	python manage.py migrate
	```

4. **Criar dados iniciais (apenas primeira vez nesse ambiente)**

	```bash
	python manage.py setup_initial_data
	python manage.py setup_disciplinas_anos
	python.manage.py setup_tags
	```

5. **Criar utilizador admin** (se ainda não existir)

	```bash
	python manage.py createsuperuser
	```

6. **(Opcional) Configurar email de notificação de aprovação**

	- Acede a `/admin/`, entra com o superuser.
	- Em “Configurações de Verificação”, define o email global que recebe notificações.
	- Em “Users”, certifica-te de que as contas `is_staff` têm o campo **Email** preenchido (recebem notificações pessoais).

---

## 🤖 Verificação por AI

Esta aplicação usa a API do Groq para verificar automaticamente ficheiros carregados (PDFs, textos, etc.) antes de os tornar públicos. A verificação é executada em `src/resumos/services/groq_guard.py` e espera a variável de ambiente `GROQ_API_KEY` configurada.

- **O que faz:** envia uma amostra do ficheiro ao modelo `meta-llama/Llama-Guard-4-12B` e recebe uma resposta curta: `safe` (seguro) ou `unsafe\n<categoria>` (inseguro + categoria).
- **Ambiente:** a função procura a chave em `GROQ_API_KEY`. Se não estiver definida, a verificação falha com a mensagem: "Chave da API do Groq não encontrada. Configure GROQ_API_KEY.".

Como configurar localmente

- Defina a variável de ambiente com a sua chave do Groq.

PowerShell:

```powershell
Copy-Item .env.example .env
notepad .env
```

Bash (Linux / macOS):

```bash
cp .env.example .env
nano .env
```

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
├── media/                 # Uploads de ficheiros
└── manage.py             # Script de gestão Django
```

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.2
- **Frontend**: HTML5, Bootstrap 5, CSS3, JavaScript
- **Base de Dados**: SQLite
- **Python**: 3.x

**© 2026 Banco de Resumos Marista - Projeto Escolar**

