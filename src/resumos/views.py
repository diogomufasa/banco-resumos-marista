from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Resumo, Disciplina, Ano, Tag
from .services.groq_guard import verify_file_with_groq, verify_text_with_groq


def signup(request):
    """
    View para registar novos utilizadores
    """
    if request.user.is_authenticated:
        messages.info(request, 'Já estás autenticado.')
        return redirect('resumos:lista')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        # Validações
        if not username or not email or not password:
            messages.error(
                request, 'Por favor, preenche todos os campos obrigatórios.')
            return render(request, 'resumos/signup.html')

        if password != password_confirm:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'resumos/signup.html')

        if len(password) < 6:
            messages.error(
                request, 'A password deve ter pelo menos 6 caracteres.')
            return render(request, 'resumos/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de utilizador já está em uso.')
            return render(request, 'resumos/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está registado.')
            return render(request, 'resumos/signup.html')

        # Verificar username, nome e apelido com Groq
        is_safe, error_message = verify_text_with_groq(
            username, label="username")
        if not is_safe:
            messages.error(
                request, f'Nome de utilizador não permitido: {error_message}')
            return render(request, 'resumos/signup.html')

        if first_name:
            is_safe, error_message = verify_text_with_groq(
                first_name, label="nome")
            if not is_safe:
                messages.error(request, f'Nome não permitido: {error_message}')
                return render(request, 'resumos/signup.html')

        if last_name:
            is_safe, error_message = verify_text_with_groq(
                last_name, label="apelido")
            if not is_safe:
                messages.error(
                    request, f'Apelido não permitido: {error_message}')
                return render(request, 'resumos/signup.html')

        # Criar utilizador
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Fazer login automaticamente
            login(request, user)
            messages.success(
                request, f'Bem-vindo, {username}! Conta criada com sucesso.')
            return redirect('resumos:lista')

        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
            return render(request, 'resumos/signup.html')

    return render(request, 'resumos/signup.html')


def lista_resumos(request):
    resumos = Resumo.objects.all()
    disciplinas = Disciplina.objects.all()
    anos = Ano.objects.all()

    disciplina_id = request.GET.get('disciplina')
    ano_id = request.GET.get('ano')
    search_query = request.GET.get('search')

    if ano_id:
        resumos = resumos.filter(ano_id=ano_id)
        disciplinas_com_ano = disciplinas.filter(anos_disponiveis__id=ano_id)
        disciplinas_sem_ano = disciplinas.filter(anos_disponiveis__isnull=True)
        disciplinas = (disciplinas_com_ano | disciplinas_sem_ano).distinct()

    if disciplina_id:
        resumos = resumos.filter(disciplina_id=disciplina_id)

    if search_query:
        resumos = resumos.filter(
            Q(titulo__icontains=search_query) |
            Q(conteudo__icontains=search_query) |
            Q(tags__nome__icontains=search_query)
        ).distinct()

    context = {
        'resumos': resumos,
        'disciplinas': disciplinas,
        'anos': anos,
        'selected_ano': ano_id,
        'selected_disciplina': disciplina_id,
        'search_query': search_query or '',
    }
    return render(request, 'resumos/lista.html', context)


def detalhe_resumo(request, pk):
    resumo = get_object_or_404(Resumo, pk=pk)
    return render(request, 'resumos/detalhe.html', {'resumo': resumo})


@login_required
def criar_resumo(request):
    disciplinas = Disciplina.objects.all()
    anos = Ano.objects.all()
    tags = Tag.objects.all()

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        conteudo = request.POST.get('conteudo')
        disciplina_id = request.POST.get('disciplina')
        ano_id = request.POST.get('ano')
        ficheiro = request.FILES.get('ficheiro')
        tag_ids = request.POST.getlist('tags')

        context = {
            'disciplinas': disciplinas,
            'anos': anos,
            'tags': tags,
            'form_data': request.POST,
            'form_selected_ano': ano_id,
            'form_selected_disciplina': disciplina_id,
            'selected_tags': tag_ids,
        }

        if not all([titulo, conteudo, disciplina_id, ano_id]):
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return render(request, 'resumos/form.html', context)

        if not ficheiro:
            messages.error(request, 'O ficheiro de resumo é obrigatório.')
            return render(request, 'resumos/form.html', context)

        is_safe_titulo, error_titulo = verify_text_with_groq(
            titulo, label="título do resumo")
        if not is_safe_titulo:
            messages.error(request, f'Título não permitido: {error_titulo}')
            return render(request, 'resumos/form.html', context)

        is_safe_text, error_text = verify_text_with_groq(
            conteudo, label="descrição do resumo")
        if not is_safe_text:
            messages.error(request, error_text)
            return render(request, 'resumos/form.html', context)

        is_safe, error_message = verify_file_with_groq(ficheiro)
        if not is_safe:
            messages.error(request, error_message)
            return render(request, 'resumos/form.html', context)

        resumo = Resumo.objects.create(
            titulo=titulo,
            conteudo=conteudo,
            disciplina_id=disciplina_id,
            ano_id=ano_id,
            autor=request.user,
            ficheiro=ficheiro
        )

        if tag_ids:
            resumo.tags.set(tag_ids)

        messages.success(request, 'Resumo criado com sucesso!')
        return redirect('resumos:detalhe', pk=resumo.pk)

    return render(request, 'resumos/form.html', {
        'disciplinas': disciplinas,
        'anos': anos,
        'tags': tags,
    })


@login_required
def editar_resumo(request, pk):
    resumo = get_object_or_404(Resumo, pk=pk)

    if resumo.autor != request.user:
        messages.error(request, 'Não tem permissão para editar este resumo.')
        return redirect('resumos:detalhe', pk=pk)

    disciplinas = Disciplina.objects.all()
    anos = Ano.objects.all()
    tags = Tag.objects.all()

    if request.method == 'POST':
        novo_titulo = request.POST.get('titulo')
        novo_conteudo = request.POST.get('conteudo')
        resumo.disciplina_id = request.POST.get('disciplina')
        resumo.ano_id = request.POST.get('ano')
        tag_ids = request.POST.getlist('tags')

        is_safe_titulo, error_titulo = verify_text_with_groq(
            novo_titulo, label="título do resumo")
        if not is_safe_titulo:
            messages.error(request, f'Título não permitido: {error_titulo}')
            return render(request, 'resumos/form.html', {
                'resumo': resumo,
                'disciplinas': disciplinas,
                'anos': anos,
                'tags': tags,
            })
        resumo.titulo = novo_titulo

        is_safe_text, error_text = verify_text_with_groq(
            novo_conteudo, label="descrição do resumo")
        if not is_safe_text:
            messages.error(request, error_text)
            return render(request, 'resumos/form.html', {
                'resumo': resumo,
                'disciplinas': disciplinas,
                'anos': anos,
                'tags': tags,
            })
        resumo.conteudo = novo_conteudo

        if request.FILES.get('ficheiro'):
            ficheiro = request.FILES.get('ficheiro')
            is_safe, error_message = verify_file_with_groq(ficheiro)
            if not is_safe:
                messages.error(request, error_message)
                return render(request, 'resumos/form.html', {
                    'resumo': resumo,
                    'disciplinas': disciplinas,
                    'anos': anos,
                    'tags': tags,
                })
            resumo.ficheiro = ficheiro

        resumo.save()

        if tag_ids:
            resumo.tags.set(tag_ids)

        messages.success(request, 'Resumo atualizado com sucesso!')
        return redirect('resumos:detalhe', pk=pk)

    return render(request, 'resumos/form.html', {
        'resumo': resumo,
        'disciplinas': disciplinas,
        'anos': anos,
        'tags': tags,
    })


@login_required
def apagar_resumo(request, pk):
    resumo = get_object_or_404(Resumo, pk=pk)

    if resumo.autor != request.user:
        messages.error(request, 'Não tem permissão para apagar este resumo.')
        return redirect('resumos:detalhe', pk=pk)

    if request.method == 'POST':
        resumo.delete()
        messages.success(request, 'Resumo apagado com sucesso!')
        return redirect('resumos:lista')

    return render(request, 'resumos/confirmar_delete.html', {'resumo': resumo})


@login_required
def perfil_usuario(request, username):
    usuario = get_object_or_404(User, username=username)
    resumos = Resumo.objects.filter(autor=usuario)

    return render(request, 'resumos/perfil.html', {
        'utilizador': usuario,
        'resumos': resumos,
    })


def get_disciplinas_por_ano(request):
    ano_id = request.GET.get('ano_id')

    if ano_id:
        disciplinas_com_ano = Disciplina.objects.filter(
            anos_disponiveis__id=ano_id)
        disciplinas_sem_ano = Disciplina.objects.filter(
            anos_disponiveis__isnull=True)
        disciplinas = (disciplinas_com_ano | disciplinas_sem_ano).distinct()
    else:
        disciplinas = Disciplina.objects.all()

    data = [{'id': d.id, 'nome': d.nome} for d in disciplinas]
    return JsonResponse({'disciplinas': data})
