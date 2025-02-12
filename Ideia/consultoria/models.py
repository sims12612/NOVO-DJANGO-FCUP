from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings

from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.models import User
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class Consultoria(models.Model):
    nome = models.CharField(max_length=100)
    especialidade = models.CharField(max_length=100)
    preco_por_hora = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilidade = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Consultor(models.Model):
    CATEGORIAS = [
        ('IT', 'IT (Tecnologia da Informação)'),
        ('SOCIAIS', 'Ciências Sociais'),
        ('EXATAS', 'Ciências Exatas'),
    ]

    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=10, choices=CATEGORIAS, default='IT')
    especialidade = models.CharField(max_length=100)
    preco_hora = models.DecimalField(max_digits=6, decimal_places=2)
    disponibilidade = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nome} - {self.get_categoria_display()}"


class User(AbstractUser, PermissionsMixin):
    objects = UserManager()  # Usando o UserManager personalizado

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    USER_TYPES = (
        ('client', 'Client'),
        ('consultant', 'Consultant'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='client')
    groups = models.ManyToManyField(Group, related_name="consultoria_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="consultoria_user_permissions", blank=True)

    def is_client(self):
        return self.user_type == 'client'

    def is_consultant(self):
        return self.user_type == 'consultant'


class Client(models.Model):
    PROFISSOES = [
        ('Ciências Exatas', 'Ciências Exatas'),
        ('Ciências Sociais', 'Ciências Sociais'),
        ('Engenheiro de Software', 'Engenheiro de Software'),
        ('Consultor de TI', 'Consultor de TI'),
        ('Consultor de Gestão', 'Consultor de Gestão'),
        ('Arquiteto de Sistemas', 'Arquiteto de Sistemas'),
        ('Desenvolvedor Frontend', 'Desenvolvedor Frontend'),
        ('Desenvolvedor Backend', 'Desenvolvedor Backend'),
        ('Engenheiro de Dados', 'Engenheiro de Dados'),
        ('Gestor de Projetos', 'Gestor de Projetos'),
        ('Administrador de Redes', 'Administrador de Redes'),
        ('Gerente de TI', 'Gerente de TI'),
        ('Gestor de Equipe', 'Gestor de Equipe'),
        ('Engenheiro Mecânico', 'Engenheiro Mecânico'),
        ('Engenheiro Elétrico', 'Engenheiro Elétrico'),
        ('Engenheiro Civil', 'Engenheiro Civil'),
        ('Médico', 'Médico'),
        ('Enfermeiro', 'Enfermeiro'),
        ('Farmacêutico', 'Farmacêutico'),
        ('Dentista', 'Dentista'),
        ('Arquiteto', 'Arquiteto'),
        ('Designer Gráfico', 'Designer Gráfico'),
        ('Artesão', 'Artesão'),
        ('Jornalista', 'Jornalista'),
        ('Psicólogo', 'Psicólogo'),
        ('Fisioterapeuta', 'Fisioterapeuta'),
        ('Pedagogo', 'Pedagogo'),
        ('Advogado', 'Advogado'),
        ('Assistente Social', 'Assistente Social'),
        ('Escriturário', 'Escriturário'),
        ('Contador', 'Contador'),
        ('Gerente de Marketing', 'Gerente de Marketing'),
        ('Publicitário', 'Publicitário'),
        ('Social Media', 'Social Media'),
        ('Gestor de Comunicação', 'Gestor de Comunicação'),
        ('Gestor de Vendas', 'Gestor de Vendas'),
        ('Vendedor', 'Vendedor'),
        ('Assistente de Vendas', 'Assistente de Vendas'),
        ('Supervisor de Vendas', 'Supervisor de Vendas'),
        ('Analista de Marketing', 'Analista de Marketing'),
        ('Designer de Interiores', 'Designer de Interiores'),
        ('Gestor de Logística', 'Gestor de Logística'),
        ('Engenheiro de Produção', 'Engenheiro de Produção'),
        ('Tecnólogo em Produção', 'Tecnólogo em Produção'),
        ('Engenheiro de Alimentos', 'Engenheiro de Alimentos'),
        ('Supervisor de Produção', 'Supervisor de Produção'),
        ('Coordenador de Produção', 'Coordenador de Produção'),
        ('Analista de Logística', 'Analista de Logística'),
        ('Gestor de Suprimentos', 'Gestor de Suprimentos'),
        ('Supervisor de Suprimentos', 'Supervisor de Suprimentos'),
        ('Engenheiro Químico', 'Engenheiro Químico'),
        ('Engenheiro Ambiental', 'Engenheiro Ambiental'),
        ('Técnico de Enfermagem', 'Técnico de Enfermagem'),
        ('Técnico em Segurança do Trabalho', 'Técnico em Segurança do Trabalho'),
        ('Técnico de Eletrônica', 'Técnico de Eletrônica'),
        ('Técnico de Informática', 'Técnico de Informática'),
        ('Estagiário', 'Estagiário'),
        ('Assistente Administrativo', 'Assistente Administrativo'),
        ('Assistente de Marketing', 'Assistente de Marketing'),
        ('Assistente de Recursos Humanos', 'Assistente de Recursos Humanos'),
        ('Assistente de Logística', 'Assistente de Logística'),
        ('Supervisor de Atendimento', 'Supervisor de Atendimento'),
        ('Gerente de Atendimento', 'Gerente de Atendimento'),
        ('Supervisor de Qualidade', 'Supervisor de Qualidade'),
        ('Engenheiro de Software Embarcado', 'Engenheiro de Software Embarcado'),
        ('Desenvolvedor Fullstack', 'Desenvolvedor Fullstack'),
        ('Desenvolvedor Mobile', 'Desenvolvedor Mobile'),
        ('Arquiteto de Software', 'Arquiteto de Software'),
        ('Desenvolvedor de Jogos', 'Desenvolvedor de Jogos'),
        ('Engenheiro de IA', 'Engenheiro de IA'),
        ('Analista de Dados', 'Analista de Dados'),
        ('Cientista de Dados', 'Cientista de Dados'),
        ('Especialista em Big Data', 'Especialista em Big Data'),
        ('Consultor de Big Data', 'Consultor de Big Data'),
        ('Engenheiro de Machine Learning', 'Engenheiro de Machine Learning'),
        ('Desenvolvedor de IA', 'Desenvolvedor de IA'),
        ('Desenvolvedor de Robótica', 'Desenvolvedor de Robótica'),
        ('Gestor de TI', 'Gestor de TI'),
        ('Consultor de Cloud Computing', 'Consultor de Cloud Computing'),
        ('Consultor de Cibersegurança', 'Consultor de Cibersegurança'),
        ('Engenheiro de Cibersegurança', 'Engenheiro de Cibersegurança'),
        ('Desenvolvedor de API', 'Desenvolvedor de API'),
        ('Desenvolvedor de Software as a Service', 'Desenvolvedor de Software as a Service'),
        ('Administrador de Banco de Dados', 'Administrador de Banco de Dados'),
        ('Suporte Técnico', 'Suporte Técnico'),
        ('Consultor de SEO', 'Consultor de SEO'),
        ('Consultor de SEM', 'Consultor de SEM'),
        ('Consultor de UX/UI', 'Consultor de UX/UI'),
        ('Gestor de Projetos Agile', 'Gestor de Projetos Agile'),
        ('Scrum Master', 'Scrum Master'),
        ('Coordenador de TI', 'Coordenador de TI'),
        ('Coordenador de Equipe', 'Coordenador de Equipe'),
        ('Engenheiro de Telecomunicações', 'Engenheiro de Telecomunicações'),
        ('Analista de Suporte', 'Analista de Suporte'),
        ('Consultor de TI', 'Consultor de TI'),
        ('Supervisor de TI', 'Supervisor de TI'),
        ('Técnico em Redes', 'Técnico em Redes'),
        ('Administrador de Sistemas', 'Administrador de Sistemas'),
        ('Gestor de Equipe de TI', 'Gestor de Equipe de TI'),
        ('Desenvolvedor de Arquitetura de Software', 'Desenvolvedor de Arquitetura de Software'),
        ('Engenheiro de Sistemas Embarcados', 'Engenheiro de Sistemas Embarcados'),
        ('Engenheiro de Infraestrutura', 'Engenheiro de Infraestrutura'),
        ('Engenheiro de Segurança', 'Engenheiro de Segurança'),
        ('Desenvolvedor de Aplicativos', 'Desenvolvedor de Aplicativos'),
        ('Consultor de ERP', 'Consultor de ERP'),
        ('Consultor de CRM', 'Consultor de CRM'),
        ('Desenvolvedor Frontend', 'Desenvolvedor Frontend'),
        ('Desenvolvedor Backend', 'Desenvolvedor Backend'),
        ('Engenheiro de Sistemas', 'Engenheiro de Sistemas'),
        ('Consultor de Infraestrutura', 'Consultor de Infraestrutura'),
        ('Consultor de Desenvolvimento', 'Consultor de Desenvolvimento'),
        ('Engenheiro de Software', 'Engenheiro de Software'),
        ('Especialista em Automação', 'Especialista em Automação'),
        ('Técnico em Automação', 'Técnico em Automação'),
        ('Engenheiro de Redes', 'Engenheiro de Redes'),
        ('Analista de Segurança da Informação', 'Analista de Segurança da Informação'),
        ('Gestor de Projetos de TI', 'Gestor de Projetos de TI'),
        ('Desenvolvedor de Games', 'Desenvolvedor de Games')
    ]
    CATEGORIAS = [
        ('IT', 'IT (Tecnologia da Informação)'),
        ('Ciências Sociais', 'Ciências Sociais'),
        ('Ciências Exatas', 'Ciências Exatas'),
    ]

    DISTRITOS = [
        ('Aveiro', 'Aveiro'),
        ('Beja', 'Beja'),
        ('Braga', 'Braga'),
        ('Bragança', 'Bragança'),
        ('Castelo Branco', 'Castelo Branco'),
        ('Coimbra', 'Coimbra'),
        ('Évora', 'Évora'),
        ('Faro', 'Faro'),
        ('Guarda', 'Guarda'),
        ('Leiria', 'Leiria'),
        ('Lisboa', 'Lisboa'),
        ('Portalegre', 'Portalegre'),
        ('Porto', 'Porto'),
        ('Santarém', 'Santarém'),
        ('Setúbal', 'Setúbal'),
        ('Viana do Castelo', 'Viana do Castelo'),
        ('Vila Real', 'Vila Real'),
        ('Viseu', 'Viseu'),
        ('Região Autónoma da Madeira', 'Região Autónoma da Madeira'),
        ('Região Autónoma dos Açores', 'Região Autónoma dos Açores'),
    ]

    ONLINE = [
        ('SIM', 'SIM'),
        ('NÃO', 'NÃO'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    primeiro_nome = models.CharField(max_length=50)
    ultimo_nome = models.CharField(max_length=50)
    categoria = models.CharField(max_length=100, choices=CATEGORIAS, default='IT')
    profissao = models.CharField(max_length=100, choices=PROFISSOES,default ='Developer')
    especialidade = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telemovel = models.CharField(max_length=15, blank=True, null=True)
    Morada = models.CharField(max_length=100, choices=DISTRITOS, blank=True, null=True)
    Online = models.CharField(max_length=3, choices=ONLINE, blank=True, null=True)
    Descricao = models.TextField(blank=True, null=True, help_text="Descreva o pedido aqui.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.primeiro_nome} {self.ultimo_nome}"


class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('cliente', 'Cliente'),
        ('consultor', 'Consultor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='cliente')

    def __str__(self):
        return f'{self.user.username} - {self.user_type}'


class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Pessoa(models.Model):
    nome = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, related_name='pessoas', on_delete=models.CASCADE)
    descricao = models.TextField()

    def __str__(self):
        return self.nome

class Especialidade(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nome} ({self.categoria.nome})'

class Pedido(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("em_andamento", "Em Andamento"),
        ("concluido", "Concluído"),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    especialidade = models.CharField(max_length=200)
    descricao = models.TextField()
    morada = models.CharField(max_length=255)
    telemovel = models.CharField(max_length=15)
    pago = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")



class Pessoa(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    telemovel = models.CharField(max_length=15)
    data_criacao = models.DateTimeField(auto_now_add=True)
    primeiro_nome = models.CharField(max_length=100)
    ultimo_nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    especialidade = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telemovel = models.CharField(max_length=15)
    morada = models.CharField(max_length=255)
    online = models.BooleanField(default=False)
    descricao = models.TextField(null=True, blank=True)
    data_pedido = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

class Pagamento(models.Model):
    consultor = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.CASCADE, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pagamento de {self.consultor.username} para categoria {self.categoria.nome}'
