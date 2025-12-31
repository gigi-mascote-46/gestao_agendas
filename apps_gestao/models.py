from django.db import models
from django.contrib.auth.models import AbstractUser
# Modelo de Utilizador Personalizado
class User(AbstractUser):
    # Definir se é Chefe ou Funcionário
    is_chef = models.BooleanField(default=False)
    departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True, blank=True)
# Departamentos da Empresa
class Departamento(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome
# Pedidos de Férias e Baixas Médicas
class PedidoFerias(models.Model):
    funcionario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    tipo = models.CharField(max_length=20, choices=[
        ('FERIAS', 'Férias'),
        ('DOENCA', 'Doença/Baixa'),
        ('CASAMENTO', 'Casamento'),
    ])
    status = models.CharField(max_length=20, default='PENDENTE') # PENDENTE, APROVADO, NEGADO
  
    # Turnos - evita que um funcionário tenha dois turnos no mesmo dia 
class Turno(models.Model):
    TIPOS = [
        ('MANHA', 'Manhã (08h-16h)'),
        ('TARDE', 'Tarde (16h-00h)'),
        ('FOLGA', 'Folga'),
    ]
    funcionario = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPOS, default='MANHA')

    class Meta:
        unique_together = ('funcionario', 'data') # Impede dois turnos no mesmo dia para a mesma pessoa