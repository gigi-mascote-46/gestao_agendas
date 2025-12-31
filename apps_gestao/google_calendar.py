import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permissões necessárias para ler/escrever na agenda
SCOPES = ['https://www.googleapis.com/auth/calendar']

def criar_evento_google(pedido):
    creds = None
    # O ficheiro token.json guarda as tuas credenciais após o primeiro login
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Procura o ficheiro credentials.json que baixaste da Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Definir o evento
    evento = {
        'summary': f'Férias: {pedido.funcionario.username}',
        'location': 'Escritório / Remoto',
        'description': f'Pedido aprovado via App de Gestão. Tipo: {pedido.tipo}',
        'start': {
            'date': pedido.data_inicio.isoformat(),
            'timeZone': 'Europe/Lisbon',
        },
        'end': {
            'date': pedido.data_fim.isoformat(),
            'timeZone': 'Europe/Lisbon',
        },
    }

    # Insere o evento na agenda principal (primary) do utilizador logado
    service.events().insert(calendarId='primary', body=evento).execute()