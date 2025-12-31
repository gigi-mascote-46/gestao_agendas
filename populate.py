import os
import django
from datetime import date, timedelta

# 1. Configurar o ambiente do Django para o script funcionar fora do servidor
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps_gestao.models import User, Departamento, PedidoFerias, Turno

def seed():
    print("🚀 A iniciar a criação de dados de teste...")

    # 2. Criar um Departamento de teste
    dept, created = Departamento.objects.get_or_create(nome="Desenvolvimento")
    if created:
        print("- Departamento 'Desenvolvimento' criado.")

    # 3. Criar um Chef (Administrador)
    if not User.objects.filter(username="chefe_ti").exists():
        User.objects.create_user(
            username="chefe_ti", 
            email="chef@empresa.com", 
            password="adminpassword",
            is_chef=True,
            departamento=dept
        )
        print("- Chef criado: chefe_ti (Senha: adminpassword)")

    # 4. Criar 5 Funcionários
    for i in range(1, 6):
        user_nome = f"funcionario_{i}"
        if not User.objects.filter(username=user_nome).exists():
            u = User.objects.create_user(
                username=user_nome,
                email=f"user{i}@empresa.com",
                password="userpassword",
                is_chef=False,
                departamento=dept
            )
            print(f"- Funcionário criado: {user_nome}")

            # 5. Gerar Turnos automáticos para esta semana para cada funcionário
            hoje = date.today()
            for d in range(7): # Próximos 7 dias
                Turno.objects.get_or_create(
                    funcionario=u,
                    data=hoje + timedelta(days=d),
                    defaults={'tipo': 'MANHA' if i % 2 == 0 else 'TARDE'}
                )
    
    print("\n✅ DADOS GERADOS COM SUCESSO!")
    print("Agora podes fazer login com 'chefe_ti' para ver o mapa preenchido.")

if __name__ == '__main__':
    seed()