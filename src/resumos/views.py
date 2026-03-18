from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from .models import Resumo, Disciplina, Ano, Tag, EmailVerificationToken, VerificationSettings
from .services.groq_guard import verify_file_with_groq, verify_text_with_groq
import secrets


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

            # Marcar como inativo até verificar o email
            user.is_active = False
            user.save(update_fields=['is_active'])

            # Criar token de verificação
            token_value = secrets.token_hex(32)
            EmailVerificationToken.objects.create(user=user, token=token_value)

            # Enviar email de verificação para o utilizador
            domain = request.get_host()
            scheme = 'https' if request.is_secure() else 'http'
            verification_url = f"{scheme}://{domain}{reverse('resumos:verificar_email', args=[token_value])}"

            subject = 'Verificação de Email - Banco de Resumos Marista'
            message = (
                f"Olá {username},\n\n"
                f"Obrigado por te registares no Banco de Resumos Marista.\n\n"
                f"Para ativares a tua conta, clica no link seguinte:\n{verification_url}\n\n"
                "Se não criaste esta conta, podes ignorar este email."
            )

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception:
                # Mesmo que o envio falhe, manter a conta criada mas inativa
                messages.warning(
                    request,
                    'Conta criada, mas houve um problema a enviar o email de verificação. '
                    'Contacta um administrador.'
                )
            else:
                messages.success(
                    request,
                    'Conta criada com sucesso! Verifica o teu email para ativares a conta. Se não receberes o email, verifica a pasta de spam ou contacta um administrador.'
                )

            # Notificar contas de administrador sobre novo utilizador para aprovação
            try:
                config = VerificationSettings.objects.first()
                config_email = config.admin_email if config and config.admin_email else None

                staff_emails = list(
                    User.objects.filter(is_staff=True, email__isnull=False)
                    .exclude(email="")
                    .values_list('email', flat=True)
                )

                recipients = set(staff_emails)
                if config_email:
                    recipients.add(config_email)

                if recipients:
                    domain = request.get_host()
                    scheme = 'https' if request.is_secure() else 'http'
                    admin_url = f"{scheme}://{domain}{reverse('admin:auth_user_change', args=[user.id])}"

                    admin_subject = 'Novo utilizador pendente de aprovação - Banco de Resumos Marista'
                    admin_message = (
                        f"Um novo utilizador registou-se e aguarda aprovação.\n\n"
                        f"Utilizador: {username}\n"
                        f"Email: {email}\n\n"
                        f"Podes rever e ativar a conta aqui:\n{admin_url}"
                    )

                    send_mail(
                        admin_subject,
                        admin_message,
                        settings.DEFAULT_FROM_EMAIL,
                        list(recipients),
                        fail_silently=True,
                    )
            except Exception:
                # Não bloquear o fluxo em caso de erro neste email
                pass

            return redirect('login')

        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
            return render(request, 'resumos/signup.html')

    return render(request, 'resumos/signup.html')


def login_view(request):
    """Login com verificação de email."""
    if request.user.is_authenticated:
        messages.info(request, 'Já estás autenticado.')
        return redirect('resumos:lista')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or ''

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(
                request, 'Nome de utilizador ou password incorretos.')
        elif not user.is_active:
            messages.warning(
                request,
                'A tua conta ainda não foi verificada. Verifica o teu email antes de entrar.'
            )
        else:
            login(request, user)
            messages.success(request, f'Bem-vindo de volta, {user.username}!')
            if next_url:
                return redirect(next_url)
            return redirect('resumos:lista')

    context = {
        'next': request.GET.get('next', ''),
    }
    return render(request, 'resumos/login.html', context)


def lista_resumos(request):
    # Apenas resumos aprovados são públicos; o autor e staff podem ver os seus pendentes
    if request.user.is_authenticated:
        if request.user.is_staff:
            resumos = Resumo.objects.all()
        else:
            resumos = Resumo.objects.filter(
                Q(is_approved=True) | Q(autor=request.user)
            )
    else:
        resumos = Resumo.objects.filter(is_approved=True)
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

    if not resumo.is_approved:
        # Apenas o autor ou staff podem ver resumos pendentes
        if not (request.user.is_authenticated and (request.user == resumo.autor or request.user.is_staff)):
            raise Http404("Resumo não encontrado")
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

        # Notificar contas de administrador sobre novo resumo pendente de aprovação
        try:
            config = VerificationSettings.objects.first()
            config_email = config.admin_email if config and config.admin_email else None

            staff_emails = list(
                User.objects.filter(is_staff=True, email__isnull=False)
                .exclude(email="")
                .values_list('email', flat=True)
            )

            recipients = set(staff_emails)
            if config_email:
                recipients.add(config_email)

            if recipients:
                domain = request.get_host()
                scheme = 'https' if request.is_secure() else 'http'
                admin_url = f"{scheme}://{domain}{reverse('admin:resumos_resumo_change', args=[resumo.id])}"

                subject = 'Novo resumo pendente de aprovação - Banco de Resumos Marista'
                message = (
                    f"Um novo resumo foi criado e aguarda aprovação.\n\n"
                    f"Título: {titulo}\n"
                    f"Autor: {request.user.username}\n"
                    f"Ano: {resumo.ano.numero}º Ano\n"
                    f"Disciplina: {resumo.disciplina.nome}\n\n"
                    f"Podes rever e aprovar o resumo aqui:\n{admin_url}"
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    list(recipients),
                    fail_silently=True,
                )
        except Exception:
            pass

        messages.success(
            request, 'Resumo criado com sucesso! Aguarda aprovação do administrador.')
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


def verificar_email(request, token):
    try:
        token_obj = EmailVerificationToken.objects.select_related(
            'user').get(token=token)
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Link de verificação inválido ou expirado.')
        return redirect('login')

    if not token_obj.is_valid():
        messages.error(request, 'Este link de verificação já não é válido.')
        return redirect('login')

    user = token_obj.user
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=['is_active'])

    if token_obj.used_at is None:
        token_obj.used_at = timezone.now()
        token_obj.save(update_fields=['used_at'])

    messages.success(
        request, 'Email verificado com sucesso! Já podes entrar na tua conta.')
    return redirect('login')
