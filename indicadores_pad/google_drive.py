#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Se conecta a una spreadsheet de Google Drive para traer todas las filas

Hay que crear credenciales propias para el proyecto siguiendo el tutorial en
https://developers.google.com/sheets/api/quickstart/python para generar un
client_secret.json con las credenciales necesarias para conectarse al Drive.

Hay que correr el script desde la línea de comandos para configurar por primera
vez las credenciales que van a ~/.credentials/ . La mejor manera de hacerlo es
agregar un ejemplo sencillo de uso de la nueva API en el main() y correrlo de
la línea de comandos.
"""
from __future__ import print_function

import os
import httplib2
from django.conf import settings

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = settings.GOOGLE_DRIVE_CREDENTIALS
APPLICATION_NAME = 'Monitoreo PAD'
CREDENTIALS_FILE = {
    "drive": 'monitoreo-pad-drive.json',
    "sheets": 'monitoreo-pad-sheets.json'
}


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-monitoreo-pad.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                                              SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Generando nuevas credenciales en ' + credential_path)
    return credentials


def get_sheets_service():
    """Usa las credenciales para crear un servicio a google sheets."""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discovery_url,
                              cache_discovery=False)
    return service


def get_sheet(spreadsheet_id, range_name):
    """Devuelve el rango de una spreadsheet como lista de listas.
    Args:
        spreadsheet_id (str): Id de la google spreadsheet
          Ej.: '1Vx0SjxnX7X-ASBJkXGWarrrnLItFTAs_TlQvxulLEak'
        range_name (str): Rango target. Ej.: 'Tiempo Real!A1:K'

    Returns:
        list: Filas de la planilla.
    """

    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    return values


def main():
    """Genera las credenciales necesarias para poder leer Google Spreadsheets.
    Este proceso es automáticamente ejecutado si se intenta abrir un
    documento sin tener credenciales guardadas en el sistema.
    """
    get_credentials()

if __name__ == '__main__':
    main()
