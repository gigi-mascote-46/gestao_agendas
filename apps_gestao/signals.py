from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PedidoFerias, User
from .notifications import notificar_chef_dia_critico
from datetime import timedelta

@receiver(post_save, sender=PedidoFerias)
def verificar_conflito_apos_aprovacao(sender, instance, **kwargs):
    # Só verificamos se o pedido acabou de ser aprovado ou é uma baixa médica
    if instance.status == 'APROVADO' or instance.tipo in ['DOENCA', 'BAIXA']:
        dept = instance.funcionario.departamento
        chef = User.objects.filter(departamento=dept, is_chef=True).first()
        
        if not chef:
            return

        total_equipa = User.objects.filter(departamento=dept).count()
        
        # Verificar cada dia do período do pedido
        data_atual = instance.data_inicio
        while data_atual <= instance.data_fim:
            ausentes = PedidoFerias.objects.filter(
                funcionario__departamento=dept,
                status='APROVADO',
                data_inicio__lte=data_atual,
                data_fim__gte=data_atual
            ).count()

            percentagem = (ausentes / total_equipa * 100) if total_equipa > 0 else 0
            
            if percentagem > 20:
                # Se o dia se tornou crítico, envia o email ao Chef
                notificar_chef_dia_critico(chef.email, data_atual, percentagem)
                break # Para não enviar 10 emails se o pedido tiver 10 dias
            
            data_atual += timedelta(days=1)