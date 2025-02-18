from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
import pandas as pd
import os
from django import forms
from .forms import ReservaForm, ConsultorForm, ClientForm,UserForm
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import csv
from .models import Client
User = get_user_model()
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
import os
import csv
from django.shortcuts import render
from .models import Client
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
import os
import logging
from .models import Client
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ClientForm
from .models import Client
import os
import csv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from consultoria.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import Pedido, Categoria
from .models import Pedido
from django.urls import reverse
from django.http import HttpResponse
import paypalrestsdk
import json
from django.http import JsonResponse
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base







# Definição do caminho do arquivo CSV
CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'consultoria', 'consultores.csv')

# Definição das categorias disponíveis
CATEGORIAS_DISPONIVEIS = {
    "IT": ["Consultoria em TI", "Consultoria em Desenvolvimento Web", "Consultoria em Tecnologia da Informação"],
    "Ciências Exatas": ["Consultoria em Engenharia", "Consultoria em Arquitetura", "Consultoria em Contabilidade"],
    "Ciências Sociais": ["Consultoria em Psicologia", "Consultoria em Recursos Humanos", "Consultoria em Educação"],
}

def welcome(request):
    return render(request, 'consultoria/welcome.html')

def lista_consultores(request):
    print("📢 A função lista_consultores foi chamada!")

    if not os.path.exists(CSV_FILE_PATH):
        print("⚠️ Arquivo CSV NÃO encontrado!")
        return render(request, 'consultoria/lista_consultores.html', {'erro': 'Arquivo CSV não encontrado.'})

    try:
        consultores = pd.read_csv(CSV_FILE_PATH, dtype=str)
        consultores = consultores.fillna('')
        print("✅ Consultores carregados:", consultores.to_dict(orient='records'))
    except Exception as e:
        print(f"⚠️ Erro ao ler o CSV: {e}")
        return render(request, 'consultoria/lista_consultores.html', {'erro': 'Erro ao ler o arquivo CSV.'})

    if consultores.empty:
        print("⚠️ Nenhum consultor encontrado no CSV!")
        return render(request, 'consultoria/lista_consultores.html', {'erro': 'Nenhum consultor encontrado no CSV.'})

    consultores.columns = consultores.columns.str.strip()

    # 🔍 Obter categoria e especialidade selecionadas
    categoria_selecionada = request.GET.get('categoria', 'Todas').strip()
    especialidade_selecionada = request.GET.get('especialidade', 'Todas').strip()
    ordem = request.GET.get('ordem', 'asc')

    print(f"📌 Categoria Selecionada: '{categoria_selecionada}'")
    print(f"📌 Especialidade Selecionada: '{especialidade_selecionada}'")

    # 🔥 Remover espaços extras para garantir filtragem correta
    consultores['categoria'] = consultores['categoria'].str.strip()
    consultores['especialidade'] = consultores['especialidade'].str.strip()

    # 🔥 Aplicar filtro de categoria
    if categoria_selecionada != "Todas":
        consultores = consultores[consultores['categoria'] == categoria_selecionada]

    # 🔥 Atualizar especialidades disponíveis para dropdown
    especialidades_disponiveis = consultores['especialidade'].unique().tolist()

    # 🔍 Aplicar filtro de especialidade
    if especialidade_selecionada != "Todas":
        consultores = consultores[consultores['especialidade'] == especialidade_selecionada]

    # 🔄 Ordenação por preço
    consultores["preco_hora"] = pd.to_numeric(consultores["preco_hora"], errors='coerce')
    consultores = consultores.sort_values(by="preco_hora", ascending=(ordem == 'asc'))

    consultores_list = consultores.to_dict(orient='records')

    return render(request, 'consultoria/lista_consultores.html', {
        'consultores': consultores_list,
        'categorias': ['Todas'] + list(CATEGORIAS_DISPONIVEIS.keys()),
        'categoria_selecionada': categoria_selecionada,
        'especialidades': ['Todas'] + especialidades_disponiveis,
        'especialidade_selecionada': especialidade_selecionada,
        'ordem': ordem
    })



def reservar_consultor(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['nome']
            email = form.cleaned_data['email']
            consultor = form.cleaned_data['consultor']
            data_hora = form.cleaned_data['data_hora']

            try:


                evento_link = adicionar_evento_google_calendar(nome, email, consultor, data_hora)

                # Enviar e-mail de confirmação para o utilizador
                send_mail(
                    subject="Confirmação da sua reserva",
                    message=f"Olá {nome},\n\nA sua reserva com o consultor {consultor} foi confirmada para o dia {data_hora}.\n\nObrigado!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )

                # (Opcional) Enviar e-mail para o administrador
                admin_email = "admin@teusite.com"
                send_mail(
                    subject="Nova reserva de consultoria",
                    message=f"O utilizador {nome} ({email}) reservou uma sessão com {consultor} para {data_hora}.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )

                return render(request, 'consultoria/reserva_confirmada.html', {'nome': nome, 'consultor': consultor, 'data_hora': data_hora})

            except Exception as e:
                print(f"⚠️ Erro ao enviar e-mails: {e}")
                return render(request, 'consultoria/erroemail.html', {'erro': 'Erro ao enviar o e-mail.'})

    return redirect('lista_consultores')

def registrar_consultor(request):
    if request.method == "POST":
        form = ConsultorForm(request.POST)
        if form.is_valid():
            novo_consultor = form.cleaned_data
            nome = novo_consultor['nome']
            especialidade = novo_consultor['especialidade']
            preco_hora = novo_consultor['preco_hora']
            disponibilidade = novo_consultor['disponibilidade']
            categoria = novo_consultor['categoria']  # 🔥 PEGA A CATEGORIA DIRETAMENTE DO FORMULÁRIO!

            # 🔥 Converte "SOCIAIS" para "Ciências Sociais" e "EXATAS" para "Ciências Exatas"
            if categoria == "SOCIAIS":
                categoria = "Ciências Sociais"
            elif categoria == "EXATAS":
                categoria = "Ciências Exatas"

            # Criar DataFrame com o novo consultor
            df_novo = pd.DataFrame([[nome, especialidade, preco_hora, disponibilidade, categoria]],
                                   columns=['nome', 'especialidade', 'preco_hora', 'disponibilidade', 'categoria'])

            if os.path.exists(CSV_FILE_PATH):
                df_novo.to_csv(CSV_FILE_PATH, mode='a', header=False, index=False)  # Adiciona ao CSV
            else:
                df_novo.to_csv(CSV_FILE_PATH, index=False)  # Cria o CSV se não existir

            print("✅ Novo consultor registrado:", df_novo.to_dict(orient='records'))
            return render(request, 'consultoria/sucesso.html', {'nome': nome})
    else:
        form = ConsultorForm()

    return render(request, 'consultoria/registrar_consultor.html', {'form': form})

from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = "https://calendar.google.com/calendar/embed?src=miguelns126%40gmail.com&ctz=UTC"  # Substitui pelo teu ID do Google Calendar

# Caminho para o ficheiro JSON com as credenciais
CREDENTIALS_FILE = os.path.join(settings.BASE_DIR, "credentials.json")

def adicionar_evento_google_calendar(nome, email, consultor, data_hora):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        service = build("calendar", "v3", credentials=credentials)

        evento = {
            "summary": f"Consulta com {consultor}",
            "description": f"Consulta agendada por {nome}. Contato: {email}",
            "start": {"dateTime": data_hora.isoformat(), "timeZone": "Europe/Lisbon"},
            "end": {"dateTime": (data_hora + datetime.timedelta(hours=1)).isoformat(), "timeZone": "Europe/Lisbon"},
            "attendees": [{"email": email}],
        }

        event_result = service.events().insert(calendarId=CALENDAR_ID, body=evento).execute()
        print(f"✅ Evento criado: {event_result.get('htmlLink')}")

        return event_result.get("htmlLink")

    except Exception as e:
        print(f"⚠️ Erro ao criar evento no Google Calendar: {e}")
        return None

def registar_client(request):
    import pandas as pd
    import os
    from django.shortcuts import render
    from .forms import ClientForm
    from django.conf import settings

    CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'consultoria', 'clientes.csv')  # Caminho do arquivo CSV

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ClientForm
from .models import Client
import pandas as pd
import os
import os
import csv
from django.shortcuts import render
from .models import Client

import os
import csv
from django.conf import settings
# Definir o caminho do arquivo CSV
# Definir o caminho do arquivo CSV
CSV_FILE_PATH = 'consultoria/clientes.csv'

import os
import csv
from django.shortcuts import render
from .models import Client
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
import os
from .models import Client
from django.conf import settings






import os
import csv
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client  # Importando o modelo Client (verifique se está correto)
from django.contrib.auth.decorators import login_required






CSV_FILE_PATH = 'consultoria/clientes.csv'
@login_required
def criar_pedido(request):
    CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'consultoria', 'clientes.csv')
    from datetime import datetime
    # Criar o diretório do CSV caso não exista
    os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)

    usuario = request.user  # Buscar usuário logado

    if request.method == 'POST':
        form = ClientForm(request.POST)

        if form.is_valid():
            data_pedido = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Formato: '2025-02-08 12:34:56'
            # Criar o registro do pedido para o CSV (não precisamos mais verificar se o cliente já existe)
            pedido_data = [
                usuario.first_name,   # Nome do usuário
                usuario.last_name,    # Sobrenome do usuário
                form.cleaned_data['categoria'],
                form.cleaned_data['especialidade'],
                usuario.email,        # Email do usuário
                form.cleaned_data['telemovel'],
                form.cleaned_data['Morada'],
                form.cleaned_data['Online'],
                form.cleaned_data['Descricao'],
                data_pedido
            ]

            # Escrever no CSV
            file_exists = os.path.isfile(CSV_FILE_PATH)

            with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Adicionar cabeçalho caso seja um arquivo novo
                if not file_exists:
                    writer.writerow(['primeiro_nome', 'ultimo_nome', 'categoria', 'especialidade', 'email', 'telemovel', 'Morada', 'Online', 'Descricao','data_pedido'])

                writer.writerow(pedido_data)

            # Mensagem de sucesso
            messages.success(request, f"✅ Sucesso! O cliente {usuario.first_name} foi registrado com sucesso!")

            # Redirecionar para a página de sucesso com os dados do pedido
            return redirect('pedidoregistadocomsucesso',
                            nome=usuario.first_name,
                            categoria=form.cleaned_data['categoria'],
                            especialidade=form.cleaned_data['especialidade'],
                            telemovel=form.cleaned_data['telemovel'],
                            morada=form.cleaned_data['Morada'],
                            descricao=form.cleaned_data['Descricao'])


        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")

    else:
        # Criar formulário e preencher automaticamente os campos do usuário
        form = ClientForm(initial={
            'primeiro_nome': usuario.first_name,
            'ultimo_nome': usuario.last_name,
            'email': usuario.email
        })
        # Desabilitar os campos de nome, sobrenome e email
        form.fields['primeiro_nome'].widget.attrs['disabled'] = True
        form.fields['ultimo_nome'].widget.attrs['disabled'] = True
        form.fields['email'].widget.attrs['disabled'] = True
    return render(request, 'consultoria/criar_pedido.html', {'form': form})

def pedidoregistadocomsucesso(request, nome,categoria,especialidade,telemovel, morada, descricao):
    subject = f"Pedido registrado com sucesso: {nome}"
    message = f"""
           ✅ Sucesso!

            O seu pedido de serviço foi registado com sucesso!

           Categoria: {categoria}
           Especialidade: {especialidade}
           telemovel: {telemovel}
           Morada: {morada}
           Descrição: {descricao}

           Agradecemos o seu pedido!
           """
    from_email = settings.DEFAULT_FROM_EMAIL  # Certifique-se de que esta variável está configurada no seu settings.py
    recipient_list = [request.user.email]  # Envia para o email do usuário logado





    return render(request, 'consultoria/pedidoregistadocomsucesso.html', {
        'nome': nome,
        'categoria': categoria,
        'especialidade': especialidade,
        'telemovel': telemovel,
        'morada': morada,
        'descricao': descricao,

    })




from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm


def dashboard(request):
    return render(request, 'consultoria/dashboard.html')



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm


def user_login(request):

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Tenta autenticar o usuário
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)

                # Enviar e-mail de boas-vindas após login
                subject = "Login Bem-sucedido"
                message = f"Olá {user.username}, você fez login com sucesso no Sistema de Consultoria!"
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]  # Enviar para o e-mail do usuário


                # Adiciona uma mensagem de sucesso
                messages.success(request, 'Login com sucesso!')

                # Redireciona para o dashboard
                return redirect('dashboard')  # 'dashboard' é a URL que você quer redirecionar
            else:
                # Usuário ou senha inválidos
                messages.error(request, 'Usuário ou senha inválidos!')
        else:
            # O formulário não foi válido
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = AuthenticationForm()

    return render(request, 'consultoria/welcome.html', {'form': form})


@login_required
def client_dashboard(request):
    return render(request, "consultoria/client_dashboard.html")

@login_required
def consultant_dashboard(request):
    return render(request, "consultoria/consultant_dashboard.html")

def user_logout(request):
    logout(request)
    return render(request, "consultoria/logout.html")

def registar_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # Salva o usuário
            user = form.save()

            # Envia e-mail de confirmação de conta criada com sucesso
            subject = "Conta Criada com Sucesso"
            message = f"Olá {user.username}, sua conta foi criada com sucesso no Sistema de Consultoria!"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]  # Enviar para o e-mail do usuário


            # Adiciona uma mensagem de sucesso
            messages.success(request, 'Conta criada com sucesso!')

            # Redireciona para a página de login
            return redirect('login')  # Redireciona para a página de login após o registro
    else:
        form = UserForm()

    return render(request, 'consultoria/registar_user.html', {'form': form})


def carregar_clientes_csv():
    CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'consultoria', 'clientes.csv')
    clientes = []
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cliente = {
                'primeiro_nome': row['primeiro_nome'],
                'ultimo_nome': row['ultimo_nome'],
                'categoria': row['categoria'],
                'especialidade': row['especialidade'],
                'email': row['email'],
                'telemovel': row['telemovel'],
                'morada': row['Morada'],
                'online': row['Online'],
                'descricao': row['Descricao'],
                'data_pedido': row['data_pedido']
            }
            clientes.append(cliente)

    return clientes

CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'consultoria', 'clientes.csv')

@login_required
def escolher_categoria(request):
    """Escolhe uma categoria válida e redireciona para pagamento"""

    # Carregar dados de clientes (ou qualquer outra fonte de dados)
    clientes = carregar_clientes_csv()
    categorias_disponiveis = set(cliente["categoria"] for cliente in clientes)  # Coletar categorias únicas

    if request.method == "POST":
        categoria_escolhida = request.POST.get('categoria', '').strip()
        num_pedidos = request.POST.get('num_pedidos', '3').strip()


        # Verifica se a categoria existe no CSV
        if categoria_escolhida not in categorias_disponiveis:
            messages.error(request, "Categoria inválida. Escolha uma categoria existente.")
            return redirect('escolher_categoria')

        # Converter num_pedidos para inteiro, tratando possíveis erros
        try:
            num_pedidos = int(num_pedidos)
        except ValueError:
            messages.error(request, "Número de pedidos inválido.")
            return redirect('escolher_categoria')

        # Definir preços válidos
        precos = {3: 10, 5: 15, 10: 25}
        preco = precos.get(num_pedidos)

        if not preco:
            messages.error(request, "Escolha um número válido de pedidos (3, 5 ou 10).")
            return redirect('escolher_categoria')

        # Redireciona para a página de pagamento
        return redirect(reverse('pagar_pedido', kwargs={'preco': preco, 'num_pedidos': num_pedidos, 'categoria': categoria_escolhida}))  # Passando data do pedido}))

    # Caso GET: apenas renderiza o template com as categorias
    return render(request, 'consultoria/escolher_categoria.html', {"categorias": categorias_disponiveis})

from datetime import datetime
@login_required


def ultimos_pedidos(request, categoria):
    pedidos = carregar_clientes_csv()  # Carregar todos os pedidos

    # Filtrar os pedidos pela categoria
    pedidos_filtrados = [pedido for pedido in pedidos if pedido['categoria'] == categoria]

    # Garantir que a data_pedido seja válida antes de tentar ordenar
    pedidos_filtrados = [
        pedido for pedido in pedidos_filtrados if pedido['data_pedido'] and isinstance(pedido['data_pedido'], str)
    ]

    # Excluir pedidos do usuário logado
    if request.user.is_authenticated:
        pedidos_filtrados = [
            pedido for pedido in pedidos_filtrados if pedido['email'] != request.user.email
        ]

    # Ordenar os pedidos pela data, se existirem dados válidos
    pedidos_filtrados.sort(key=lambda pedido: datetime.strptime(pedido['data_pedido'], '%Y-%m-%d %H:%M:%S') if pedido['data_pedido'] else datetime.min, reverse=True)

    return pedidos_filtrados
CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'pedidosdv_pagos.csv')  # Caminho do arquivo CSV

def salvar_pedido_csv(pedido_id, email, especialidade, data_pedido, preco):
    """ Salva o pedido no arquivo CSV """
    CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'pedidosdv_pagos.csv')
    file_exists = os.path.isfile(CSV_FILE_PATH)  # Verifica se o arquivo já existe

    with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ['pedido_id', 'email', 'especialidade', 'data_pedido', 'preco', 'status']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Escreve o cabeçalho se o arquivo for novo

        writer.writerow({
            'pedido_id': pedido_id,
            'email': email,
            'especialidade': especialidade,
            'data_pedido': data_pedido,
            'preco': preco,
            'status': 'Pago'
        })


def carregar_pedidos_pagos():
    CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'pedidosdv_pagos.csv')
    pedidos = []

    if os.path.isfile(CSV_FILE_PATH):  # Verifica se o arquivo existe
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Verifica se 'data_pedido' existe e se não está vazio
                    if 'data_pedido' in row and row['data_pedido']:
                        row['data_pedido'] = datetime.fromisoformat(row['data_pedido'])  # Converte para datetime
                    else:
                        row['data_pedido'] = None  # Caso o 'data_pedido' não exista ou seja inválido
                except ValueError as e:
                    print(f"Erro ao converter a data do pedido {row.get('pedido_id')}: {e}")
                    row['data_pedido'] = None  # Defina como None se houver erro na conversão

                pedidos.append(row)  # Adiciona cada linha do CSV à lista

        # Ordenar os pedidos pela 'data_pedido' (do mais recente para o mais antigo)
        pedidos_ordenados = sorted(pedidos,
                                   key=lambda x: x['data_pedido'] if x['data_pedido'] is not None else datetime.min,
                                   reverse=True)

    return pedidos_ordenados
@login_required
def pagar_pedido(request, preco, num_pedidos, categoria):
    from django.utils.timezone import now
    """
    Função que lida com o pagamento do pedido de consultoria.
    """
    # Carregar os clientes do CSV

    clientes = carregar_clientes_csv()

    # Obter o pedido_id e valor_a_pagar via URL
    pedido_id = request.GET.get('pedido_id')  # Recebe o pedido_id da URL
    valor_a_pagar = request.GET.get('valor_a_pagar')  # Recebe o valor_a_pagar da URL
    email = request.GET.get('email') or (request.user.email if request.user.is_authenticated else "Email não fornecido")
    timestamp_str = request.POST.get("timestamp", now().isoformat())

    # Converter a string de timestamp para um objeto datetime
    timestamp = datetime.fromisoformat(timestamp_str)

    # Formatar o timestamp no formato desejado
    timestamp_formatada = timestamp.strftime('%Y-%m-%d %H:%M:%S')


    # Debug: Verifique os parâmetros passados
    print(f"Pedido ID: {pedido_id}")
    print(f"Valor a Pagar: {valor_a_pagar}")
    print(f"tempo: {timestamp}")

    # Simulação de pagamento sem real API PayPal
    if request.method == 'POST':
        # Simula pagamento bem-sucedido
        pagamento_realizado = True  # Simulando que o pagamento foi bem-sucedido

        if pagamento_realizado:
            pedido = Pedido.objects.filter(id=pedido_id).first()
            print(f"Pedido encontrado: {pedido}")  # Imprime o objeto Pedid

            if pedido:
                data_pedido = timestamp_formatada
                print(f" Data do Pedido: {data_pedido}")  # Verificar os valores
            else:
                data_pedido = timestamp_formatada
            print("Pagamento realizado com sucesso!")
            print(f"Salvando no CSV: {pedido_id}, {email}, {categoria}, {data_pedido}, {preco}")

            salvar_pedido_csv(pedido_id, email,categoria, data_pedido, preco)
            # Carregar os últimos pedidos após simular pagamento
            pedidos = ultimos_pedidos(request, categoria)
             # Enviar e-mail de confirmação de pagamento
            subject = 'Pagamento Confirmado!'
            message = f'O pagamento do seu pedido foi processado com sucesso. Detalhes: \n\nPreço: {preco} \nData do Pedido: {data_pedido}\nCategoria: {categoria}' #PODIA MOSTRAR OS PEDIDOS E OS DETALHES
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]




            # Redireciona para a página de pedidos após pagamento bem-sucedido
            return render(request, 'consultoria/pedidos_confirmados.html', {
                'preco': preco,
                'num_pedidos': num_pedidos,
                'categoria': categoria,
                'pedidos': pedidos,
                'data_pedido': data_pedido,
            })
        else:
            # Caso o pagamento falhe, pode exibir uma mensagem de erro
            print("Pagamento falhou")
            messages.error(request, "O pagamento não foi bem-sucedido. Tente novamente.")
            return redirect('escolher_categoria')

    # Renderiza a página de pagamento (exibição inicial)
    return render(request, 'consultoria/pagar_pedido.html', {
        'preco': preco,
        'num_pedidos': num_pedidos,
        'categoria': categoria,
    })

def processar_pagamento(valor):
    """Simula o processo de pagamento, retornando True ou False"""
    sucesso = random.choice([True, False])  # Simulação com 50% de chance de sucesso
    return sucesso
# Ver Últimos Pedidos (somente para consultores)

def processar_pagamento(request, preco, num_pedidos, categoria):
    # Configurar o pagamento
    pagamento = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri("/pagamento/sucesso/"),
            "cancel_url": request.build_absolute_uri("/pagamento/cancelado/")
        },
        "transactions": [{
            "amount": {
                "total": f"{preco}",
                "currency": "EUR"
            },
            "description": f"Pagamento por {num_pedidos} pedidos na categoria {categoria}"
        }]
    })

    # Executar a criação do pagamento
    if pagamento.create():
        # Encontrar o link de aprovação e redirecionar
        for link in pagamento.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return redirect(approval_url)
    else:
        return HttpResponse("Erro ao criar o pagamento.")

def pagamento_sucesso(request):
    # Mapear o número de pedidos para o preço correspondente
    precos = {
        3: 10,  # 3 pedidos = 10€
        5: 15,  # 5 pedidos = 15€
        10: 25  # 10 pedidos = 25€
    }

    # Carregar os clientes do CSV
    clientes = carregar_clientes_csv()

    # Filtrar os clientes pela categoria
    clientes_filtrados = [cliente for cliente in clientes if cliente['categoria'] == categoria]

    # Pegar os últimos pedidos de acordo com o número escolhido
    pedidos = clientes_filtrados[-num_pedidos:]

    # Obter o preço correto baseado no número de pedidos
    preco = precos.get(num_pedidos)

    for pedido in pedidos:
        primeiro_nome = pedido.get('primeiro_nome', '')
        ultimo_nome = pedido.get('ultimo_nome', '')
        print(f"Nome: {primeiro_nome} {ultimo_nome}")

    if not preco:
        messages.error(request, "Número de pedidos inválido ou não disponível.")
        return redirect('escolher_categoria')  # Ou redireciona para uma página de erro

    # Passar os dados para o template de sucesso
    return render(request, 'consultoria/pedidos_confirmados.html', {
        'pedidos': pedidos,
        'categoria': categoria,
        'num_pedidos': num_pedidos,
        'preco': preco
    })

def pagamento_cancelado(request):
    return HttpResponse("O pagamento foi cancelado.")
from datetime import datetime


@login_required
def pedidos_visualizacao_servicos(request):
    from django.shortcuts import render
    usuario = request.user  # Usuário autenticado
    email_usuario = usuario.email  # Obtém o e-mail do usuário logado

    pedidos = carregar_pedidos_pagos()  # Carregar os pedidos do CSV

    # Filtrar pedidos que correspondem ao e-mail do usuário logado
    pedidos_filtrados = [pedido for pedido in pedidos if pedido['email'] == email_usuario]

    return render(request, 'consultoria/pedidos_visualizacao_servicos.html', {'pedidos': pedidos_filtrados})


    import os
    import csv
    from datetime import datetime
    from django.conf import settings
    from django.shortcuts import render
    from .models import Pedido
from django.shortcuts import render

def meus_servicos_pedidos(request):
    usuario = request.user
    print(f"Usuário autenticado: {usuario} (Email: {usuario.email})")

    pedidos = Pedido.objects.filter(usuario=usuario).order_by('-data_criacao')

    print(f"Pedidos encontrados no banco: {len(pedidos)}")

    pedidos_db = [
        {
            'id': pedido.id,
            'especialidade': pedido.especialidade,
            'status': pedido.status,
            'data_pedido': pedido.data_criacao,
            'usuario_id': pedido.usuario.id,
        }
        for pedido in pedidos
    ]

    CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'consultoria', 'clientes.csv')
    pedidos_csv = []

    if os.path.isfile(CSV_FILE_PATH):
        try:
            with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if reader.fieldnames is None:
                    print("Erro: O arquivo CSV não contém cabeçalhos válidos.")
                else:
                    for row in reader:
                        if row.get('email', '').strip().lower() == usuario.email.strip().lower():
                            row['status'] = 'Pendente'
                            pedidos_csv.append(row)
        except Exception as e:
            print(f"Erro ao ler o CSV: {e}")

    pedidos_combined = pedidos_db + pedidos_csv

    for pedido in pedidos_combined:
        if isinstance(pedido.get('data_pedido'), str):
            try:
                pedido['data_pedido'] = datetime.strptime(pedido['data_pedido'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print(f"Erro ao converter data: {pedido['data_pedido']}")
                pedido['data_pedido'] = datetime.min

    pedidos_combined.sort(key=lambda x: x.get('data_pedido') or datetime.min, reverse=True)

    print(f"Total de pedidos exibidos: {len(pedidos_combined)}")

    return render(request, 'consultoria/meus_servicos_pedidos.html', {'pedidos': pedidos_combined})


@login_required
def area_consultor(request):
    return render(request, 'consultoria/area_consultor.html')
@login_required
def area_cliente(request):
    usuario = request.user
    pedidos = Pedido.objects.filter(usuario=usuario)  # Filtra os pedidos do usuário logado
    return render(request, 'consultoria/area_cliente.html', {'pedidos': pedidos})



logger = logging.getLogger(__name__)
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

from django.http import JsonResponse
import json
from datetime import datetime
import os
import csv
from .models import Pedido  # Importe o modelo Pedido corretamente

def marcar_concluido(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pessoa_id = data.get('pessoa_id')
            print(f"ID da pessoa recebido: {pessoa_id}")  # Verifique o ID recebido

            if not pessoa_id:
                return JsonResponse({'error': 'ID da pessoa ausente'}, status=400)

            pessoa = Pessoa.objects.get(id=pessoa_id)
            print(f"Pessoa encontrada: {pessoa}")  # Verifique se a pessoa foi encontrada

            pedido = Pedido.objects.filter(usuario=pessoa).first()
            if pedido:
                pedido.status = 'Concluído'
                pedido.save()
                print(f"Pedido marcado como concluído: {pedido.id}")  # Confirmação de que o pedido foi atualizado
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Pedido não encontrado'}, status=404)

        except Pessoa.DoesNotExist:
            return JsonResponse({'error': 'Pessoa não encontrada'}, status=404)
        except Exception as e:
            print(f"Erro no backend: {e}")  # Detalhes do erro
            return JsonResponse({'error': str(e)}, status=500)
