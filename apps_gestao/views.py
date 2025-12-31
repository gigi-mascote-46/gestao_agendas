from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import calendar
from datetime import date, timedelta # Adicionado timedelta

# Importamos os formulários, modelos e serviços
from .forms import CustomUserCreationForm, PedidoFeriasForm
from .models import PedidoFerias, User, Turno  # Adicionado Turno
from .services import validar_ferias
from .google_calendar import criar_evento_google

@login_required
def dashboard(request):
    """
    Dashboard inteligente: Gerencia pedidos de férias, analisa conflitos operacionais
    e permite ao Chef validar novos registos de utilizadores.
    """
    user = request.user
    context = {}

    if user.is_chef:
        # 1. PEDIDOS DE FÉRIAS PENDENTES
        # Filtramos pedidos que aguardam aprovação no departamento do Chef
        context['pedidos_pendentes'] = PedidoFerias.objects.filter(
            funcionario__departamento=user.departamento, 
            status='PENDENTE'
        )
        
        # 2. NOVOS UTILIZADORES AGUARDANDO VALIDAÇÃO (Regra Tech-Security)
        # Filtramos apenas utilizadores 'is_active=False' do mesmo departamento
        context['utilizadores_inativos'] = User.objects.filter(
            departamento=user.departamento,
            is_active=False
        ).order_by('-date_joined')

        # 3. LÓGICA DO DASHBOARD DE CONFLITOS (Próximos 14 dias)
        hoje = date.today()
        dias_analise = []
        
        # IMPORTANTE: No cálculo da equipa, contamos apenas utilizadores já ATIVOS
        total_equipa = User.objects.filter(
            departamento=user.departamento, 
            is_active=True
        ).count()

        for i in range(14):
            dia = hoje + timedelta(days=i)
            ausentes = PedidoFerias.objects.filter(
                funcionario__departamento=user.departamento,
                status='APROVADO',
                data_inicio__lte=dia,
                data_fim__gte=dia
            ).count()

            # Cálculo da percentagem crítica baseada na capacidade real (staff ativo)
            percentagem = (ausentes / total_equipa * 100) if total_equipa > 0 else 0
            
            dias_analise.append({
                'data': dia,
                'ausentes': ausentes,
                'critico': percentagem >= 20 
            })
        
        context['calendario_conflitos'] = dias_analise
        context['todos_funcionarios'] = User.objects.filter(
            departamento=user.departamento, 
            is_active=True
        )
        
    else:
        # 4. VISTA DO FUNCIONÁRIO
        # Mostra o histórico pessoal por ordem de data
        context['meus_pedidos'] = PedidoFerias.objects.filter(
            funcionario=user
        ).order_by('-data_inicio')

    return render(request, 'dashboard.html', context)

# ADICIONA ESTA FUNÇÃO PARA O BOTÃO DO DASHBOARD FUNCIONAR
@login_required
def ativar_utilizador(request, user_pk):
    """
    Permite ao Chef ativar contas de novos funcionários do seu departamento.
    """
    if not request.user.is_chef:
        messages.error(request, "Acesso negado. Apenas administradores podem validar registos.")
        return redirect('dashboard')

    # get_object_or_404 é mais seguro do que .get()
    usuario_a_ativar = get_object_or_404(User, pk=user_pk)
    
    # Segurança adicional: Só ativa utilizadores do mesmo departamento
    if usuario_a_ativar.departamento == request.user.departamento:
        usuario_a_ativar.is_active = True
        usuario_a_ativar.save()
        messages.success(request, f"O utilizador {usuario_a_ativar.username} foi ativado com sucesso!")
    else:
        messages.error(request, "Não tens permissão para ativar utilizadores de outros departamentos.")
        
    return redirect('dashboard')

# 2. VISTA DE NOVO PEDIDO DE FÉRIAS
@login_required
def novo_pedido(request):
    if request.method == 'POST':
        form = PedidoFeriasForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.funcionario = request.user
            
            # Validação das Regras de Negócio (20% e Substituição)
            permitido, mensagem = validar_ferias(
                pedido.funcionario, 
                pedido.data_inicio, 
                pedido.data_fim
            )
            
            if permitido:
                pedido.save()
                messages.success(request, "Pedido enviado com sucesso!")
                return redirect('dashboard')
            else:
                messages.error(request, mensagem)
    else:
        form = PedidoFeriasForm()
    return render(request, 'novo_pedido.html', {'form': form})

# 3. APROVAÇÃO E INTEGRAÇÃO GOOGLE
@login_required
def aprovar_pedido(request, pedido_id):
    if not request.user.is_chef:
        messages.error(request, "Acesso negado.")
        return redirect('dashboard')

    pedido = get_object_or_404(PedidoFerias, id=pedido_id)
    pedido.status = 'APROVADO'
    pedido.save()

    try:
        criar_evento_google(pedido)
        messages.success(request, f"Aprovado e sincronizado com Google Calendar!")
    except Exception as e:
        messages.warning(request, f"Aprovado localmente, mas erro no Google: {e}")

    return redirect('dashboard')

# 4. REJEIÇÃO
@login_required
def recusar_pedido(request, pedido_id):
    if not request.user.is_chef:
        return redirect('dashboard')
    pedido = get_object_or_404(PedidoFerias, id=pedido_id)
    pedido.status = 'NEGADO'
    pedido.save()
    messages.info(request, "Pedido recusado.")
    return redirect('dashboard')

# 5. VISTA DE REGISTO DE UTILIZADOR (Alterada)
def register(request):
    # Se já estiver logado, não deve ver a página de registo
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # NÃO SALVAMOS LOGO NA BD. Usamos commit=False
            user = form.save(commit=False)
            
            # O SEGREDO: definimos o utilizador como INATIVO
            user.is_active = False 
            user.save()
            
            # Mensagem de sucesso e redireciona para o Login (sem fazer login automático!)
            messages.success(request, "Conta criada com sucesso! Aguarda a validação do Chef do teu departamento para poderes entrar.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# 6. MAPA VISUAL DE FÉRIAS E TURNOS
@login_required
def mapa_ferias(request):
    if not request.user.is_chef:
        return redirect('dashboard')

    hoje = date.today()
    num_dias = calendar.monthrange(hoje.year, hoje.month)[1]
    dias_do_mes = range(1, num_dias + 1)
    funcionarios = User.objects.filter(departamento=request.user.departamento)

    mapa = []
    for f in funcionarios:
        dados_dias = []
        for dia in dias_do_mes:
            data_v = date(hoje.year, hoje.month, dia)
            
            ausencia = PedidoFerias.objects.filter(
                funcionario=f, status='APROVADO',
                data_inicio__lte=data_v, data_fim__gte=data_v
            ).first()

            turno = Turno.objects.filter(funcionario=f, data=data_v).first()

            if ausencia:
                conteudo = {'classe': 'bg-success text-white', 'texto': 'F'}
            elif turno:
                classe = 'bg-primary text-white' if turno.tipo == 'MANHA' else 'bg-info text-dark'
                conteudo = {'classe': classe, 'texto': turno.tipo[0]}
            else:
                conteudo = {'classe': 'bg-light', 'texto': '-'}
                
            dados_dias.append(conteudo)
        
        mapa.append({'nome': f.username, 'id': f.pk, 'dias': dados_dias})

    return render(request, 'mapa_ferias.html', {'mapa': mapa, 'dias_do_mes': dias_do_mes})

# 7. ATRIBUIÇÃO DE TURNOS (Ação do formulário no Mapa)
@login_required
def atribuir_turno(request):
    if request.method == 'POST' and request.user.is_chef:
        func_id = request.POST.get('funcionario')
        data_inicio = request.POST.get('data_inicio')
        tipo = request.POST.get('tipo')
        
        funcionario = User.objects.get(pk=func_id)
        data_dt = date.fromisoformat(data_inicio)
        
        # Atribui para a semana de trabalho (5 dias)
        for i in range(5):
            dia = data_dt + timedelta(days=i)
            Turno.objects.update_or_create(
                funcionario=funcionario, data=dia,
                defaults={'tipo': tipo}
            )
        messages.success(request, f"Turnos atribuídos com sucesso!")
    return redirect('mapa_ferias')