# 📅 Workforce Manager Pro: Gestão Inteligente de Turnos e Férias

Este é um sistema de **Workforce Management (WFM)** robusto desenvolvido em **Python & Django**. Foi desenhado para resolver problemas reais de logística de equipas, garantindo que nenhum departamento fique abaixo da capacidade operacional mínima.

[Image of a professional software architecture diagram for a Python Django web application with external API integrations]

## 🌟 Diferenciais Técnicos

* **Motor de Regras Complexas:** Validação automática de pedidos de férias baseada no tamanho da equipa (Regra dos 20% e Regra de Substituição 1:1).
* **Algoritmo de Sugestão:** Se um pedido for negado, o sistema sugere a data disponível mais próxima.
* **Integração Google Calendar:** Sincronização bi-direcional via API oficial da Google (OAuth2).
* **Visualização de Matriz:** Mapa de férias e turnos dinâmico, adaptável a qualquer mês do ano.
* **Alertas Críticos:** Monitorização proativa que sinaliza dias de risco operacional ao gestor.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.x, Django Framework.
* **Base de Dados:** PostgreSQL (Produção) / SQLite (Desenvolvimento).
* **Frontend:** Bootstrap 5, HTML5, CSS3.
* **APIs:** Google Calendar API v3.

## 📂 Estrutura do Projeto

```text
gestao_agendas/
├── apps_gestao/        # Lógica principal da aplicação
│   ├── models.py       # Definição de Users, Departamentos, Pedidos e Turnos
│   ├── services.py     # O "Cérebro" - Algoritmos de validação e sugestão
│   ├── signals.py      # Automação de notificações críticas
│   └── google_calendar.py # Integração com API externa
├── core/               # Configurações do projeto Django
├── templates/          # Interface do utilizador (Dashboard, Mapa, Login)
└── manage.py           # Utilitário de comando Django

🚀 Como Executar
1. Instale as dependências: pip install -r requirements.txt
2. Configure o seu credentials.json na raiz.
3. Execute: python manage.py migrate
4. Inicie: python manage.py runserver

---

### 2. Script para Gerar Dados de Teste (`populate.py`)

Cria um ficheiro chamado `populate.py` na raiz do projeto. Este script vai criar um departamento, um Chef e 5 funcionários com turnos já marcados.

````python

import os
import django
from datetime import date, timedelta

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps_gestao.models import User, Departamento, PedidoFerias, Turno

def seed():
    print("Iniciando a criação de dados de teste...")

    # 1. Criar Departamento
    dept, _ = Departamento.objects.get_or_create(nome="Desenvolvimento")

    # 2. Criar Chef
    if not User.objects.filter(username="chefe_ti").exists():
        chef = User.objects.create_user(
            username="chefe_ti", 
            email="chef@empresa.com", 
            password="adminpassword",
            is_chef=True,
            departamento=dept
        )
        print("- Chef criado: chefe_ti (senha: adminpassword)")

    # 3. Criar 5 Funcionários
    funcionarios = []
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
            funcionarios.append(u)
            print(f"- Funcionário criado: {user_nome}")

    # 4. Gerar alguns Turnos para esta semana
    hoje = date.today()
    for f in User.objects.filter(is_chef=False):
        for d in range(5):
            Turno.objects.get_or_create(
                funcionario=f,
                data=hoje + timedelta(days=d),
                tipo='MANHA' if f.id % 2 == 0 else 'TARDE'
            )
    
    print("--- DADOS GERADOS COM SUCESSO! ---")

if __name__ == '__main__':
    seed()
````