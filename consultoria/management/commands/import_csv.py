import csv
import os
from django.core.management.base import BaseCommand
from consultoria.models import Pessoa  # Ajuste para o nome correto do seu modelo

class Command(BaseCommand):
    help = 'Importa dados de um arquivo CSV para o banco de dados'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(os.path.dirname(__file__), 'C:\\Users\\utilizador\\PycharmProjects\\G\\Ideia\\consultoria\\clientes.csv')  # Ajuste o caminho do CSV

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                Pessoa.objects.create(
                    primeiro_nome=row['primeiro_nome'],
                    ultimo_nome=row['ultimo_nome'],
                    categoria=row['categoria'],
                    especialidade=row['especialidade'],
                    email=row['email'],
                    telemovel=row['telemovel'],
                    morada=row['Morada'],
                    online=row['Online'] == "SIM",  # Converte para booleano
                    descricao=row['Descricao'],
                    data_pedido=row['data_pedido'] if row['data_pedido'] else None,
                    status=row['status'] if row['status'] else None
                )

        self.stdout.write(self.style.SUCCESS('Importação concluída com sucesso!'))





