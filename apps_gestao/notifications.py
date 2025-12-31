from django.core.mail import send_mail
from django.conf import settings

def notificar_chef_dia_critico(chef_email, dia, percentagem):
    assunto = f"⚠️ ALERTA CRÍTICO: Equipa desfalcada em {dia.strftime('%d/%m/%Y')}"
    mensagem = (
        f"Olá Chef,\n\n"
        f"Este é um aviso automático. No dia {dia.strftime('%d/%m/%Y')}, "
        f"a percentagem de ausências atingiu os {percentagem:.1f}%.\n"
        f"O limite de segurança de 20% foi ultrapassado.\n\n"
        f"Por favor, verifica o Dashboard para gerir os turnos."
    )
    
    # O Django envia o email usando as configurações que definiremos no settings.py
    send_mail(
        assunto,
        mensagem,
        settings.DEFAULT_FROM_EMAIL,
        [chef_email],
        fail_silently=False,
    )