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
import argparse
import httplib2

from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    FLAGS = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except Exception:
    FLAGS = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = {
    'drive': 'https://www.googleapis.com/auth/drive',
    'sheets': 'https://www.googleapis.com/auth/spreadsheets.readonly'
}
CLIENT_SECRET_FILE = {
    'drive': 'scripts/drive/client_secret_drive.json',
    'sheets': 'scripts/drive/client_secret_sheets.json'
}
APPLICATION_NAME = 'Nombre de la aplicación'
CREDENTIALS_FILE = {
    "drive": 'nombre-aplicacion-drive.json',
    "sheets": 'nombre-aplicacion-sheets.json'
}
GDOCS_TYPES = {
    "spreadsheet": 'application/vnd.google-apps.spreadsheet'
}


def get_credentials(api="drive"):
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Args:
        api (str): Puede ser "drive" o "sheets".
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, CREDENTIALS_FILE[api])

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE[api],
                                              SCOPES[api])
        flow.user_agent = APPLICATION_NAME
        if FLAGS:
            credentials = tools.run_flow(flow, store, FLAGS)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)

    return credentials


def get_sheets_service():
    """Usa las credenciales para crear un servicio a google sheets."""
    credentials = get_credentials("sheets")
    http = credentials.authorize(httplib2.Http())
    discovery_url = ('https://sheets.googleapis.com/$discovery/rest?'
                     'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discovery_url)
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


def get_drive_service():
    """Usa las credenciales para crear un servicio a google drive."""
    credentials = get_credentials("drive")
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    return service


def update_drive_file(local_path, gdrive_id, convert_gdocs=None):
    """Actualiza el contenido de un archivo en Drive subiendo uno nuevo.

    Args:
        local_path (str): Path local al nuevo archivo a subir.
        gdrive_id (str): Id del archivo a actualizar en el drive.
        convert_gdocs (bool): Convierte el archivo a google docs.

    Returns:
        dict: Resultado de la llamada a la API.
    """
    files = get_drive_service().files()

    # sube el archivo en su formato original
    if not convert_gdocs or convert_gdocs not in GDOCS_TYPES:
        media = local_path

    # convierte a formato de google docs
    else:
        # TODO: tomar los mimeType del formato del archivo original
        media = MediaFileUpload(
            local_path,
            mimetype='application/'
                     'vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=False)

    print("Actualizando archivo", gdrive_id)
    res = files.update(fileId=gdrive_id, media_body=media).execute()

    return res


def is_file_in_folder(file_name, gdrive_dir_id):
    """Chequea que un archivo está en una carpeta del Drive.
    Args:
        file_name (str): Nombre del archivo.
        gdrive_dir_id (str): Id de una carpeta en el Drive.
    """
    files = get_drive_service().files()
    filter_query = "'{}' in parents".format(gdrive_dir_id)
    gdrive_dir_files = {f["name"]: f["id"] for f in
                        files.list(q=filter_query).execute()["files"]}

    if file_name in gdrive_dir_files:
        return gdrive_dir_files[file_name]
    else:
        return None


def create_drive_file(local_path, gdrive_dir_id, convert_gdocs=None):
    """Crea un nuevo archivo en una carpeta del drive.
    Args:
        local_path (str): Path local al nuevo archivo a subir.
        gdrive_dir_id (str): Id del directorio que contiene el archivo a crear
            o a actualizar en el drive.
        convert_gdocs (str): Indica un tipo de archivo de google docs para
            convertir.

    Returns:
        dict: Resultado de la llamada a la API.
    """
    files = get_drive_service().files()

    # sube el archivo en su formato original
    if not convert_gdocs or convert_gdocs not in GDOCS_TYPES:
        file_metadata = {
            "parents": [gdrive_dir_id],
            "name": local_path.split(os.path.sep)[-1]
        }
        media = local_path

    # convierte a formato de google docs
    else:
        file_metadata = {
            "parents": [gdrive_dir_id],
            'name': "".join(local_path.split(os.path.sep)[-1].split(".")[:-1]),
            'mimeType': GDOCS_TYPES[convert_gdocs]
        }
        # TODO: tomar los mimeType del formato del archivo original
        media = MediaFileUpload(
            local_path,
            mimetype='application/'
                     'vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=False)

    print("Creando archivo", file_metadata["name"])
    res = files.create(
        body=file_metadata, media_body=media, fields="id").execute()

    return res


def create_or_update_drive_file(local_path, gdrive_dir_id, convert_gdocs=None):
    """Actualiza o crea un archivo en Drive.
    Args:
        local_path (str): Path local al nuevo archivo a crear o actualizar.
        gdrive_dir_id (str): Id del directorio que contiene el archivo a crear
            o a actualizar en el drive.
        convert_gdocs (str): Indica un tipo de archivo de google docs para
            convertir.
    Returns:
        dict: Resultado de la llamada a la API.
    """
    file_name = local_path.split(os.path.sep)[-1]

    if convert_gdocs and convert_gdocs in GDOCS_TYPES:
        file_name = "".join(file_name.split(".")[:-1])

    gdrive_id = is_file_in_folder(file_name, gdrive_dir_id)

    if gdrive_id:
        update_drive_file(local_path, gdrive_id, convert_gdocs=convert_gdocs)
    else:
        create_drive_file(local_path, gdrive_dir_id,
                          convert_gdocs=convert_gdocs)


def main():
    pass


if __name__ == '__main__':
    main()
