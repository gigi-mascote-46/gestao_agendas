from datetime import timedelta
from .models import User, PedidoFerias

def validar_ferias(funcionario, data_inicio, data_fim):
    dept = funcionario.departamento
    total_equipa = User.objects.filter(departamento=dept).count()
    
    # Buscar todos os pedidos aprovados ou baixas que colidam com estas datas
    conflitos = PedidoFerias.objects.filter(
        funcionario__departamento=dept,
        status='APROVADO',
        data_inicio__lte=data_fim,
        data_fim__gte=data_inicio
    )

    num_ausentes = conflitos.count()

    # REGRA 1: Departamentos pequenos (<= 2 pessoas)
    if total_equipa <= 2:
        if num_ausentes >= 1:
            return False, "Regra de Substituição: O teu colega já está fora nestas datas."

    # REGRA 2: Limite de 20% (para equipas maiores)
    else:
        # Contamos +1 (o próprio funcionário que está a pedir)
        percentagem = ((num_ausentes + 1) / total_equipa) * 100
        if percentagem > 20:
            sugestao = sugerir_proxima_data(funcionario, data_inicio, (data_fim - data_inicio).days)
            return False, f"Limite de 20% excedido. Próxima data livre sugerida: {sugestao}"

    return True, "Pedido Validado com Sucesso!"

def sugerir_proxima_data(funcionario, data_tentativa, duracao):
    """
    Tenta encontrar o próximo buraco disponível avançando dia a dia.
    """
    nova_data = data_tentativa + timedelta(days=1)
    for _ in range(30): # Tenta nos próximos 30 dias
        valido, _ = validar_ferias(funcionario, nova_data, nova_data + timedelta(days=duracao))
        if valido:
            return nova_data
        nova_data += timedelta(days=1)
    return "Nenhuma data disponível brevemente."