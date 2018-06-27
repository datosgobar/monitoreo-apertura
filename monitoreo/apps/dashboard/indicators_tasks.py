# coding=utf-8
from __future__ import unicode_literals

import json
from django.conf import settings
from django.utils import timezone
from django.db.utils import DataError
from django_rq import job

from pydatajson.core import DataJson

from .models import IndicatorsGenerationTask, TableColumn, IndicatorType, Indicador, IndicadorRed
from .helpers import load_catalogs

URL = "https://raw.githubusercontent.com/datosgobar/libreria-catalogos/master/"
CENTRAL = URL + 'datosgobar/data.json'


def indicators_run():
    task = IndicatorsGenerationTask.objects.create()
    generate_indicators.delay(task.pk)


@job('indexing')
def generate_indicators(task_id):
    data_json = DataJson()
    catalogs = load_catalogs(URL)
    indics, network_indics = data_json.generate_catalogs_indicators(
        catalogs,
        CENTRAL)
    names = []
    for catalog in catalogs:
        # Obtengo el nombre de los catálogos a partir de la validación
        validation = data_json.validate_catalog(catalog)
        catalog_name = validation['error']['catalog']['title']
        names.append(catalog_name)

    task = IndicatorsGenerationTask.objects.get(pk=task_id)
    save_indicators(indics, names, task)
    save_network_indics(network_indics, 'RED', task)

    # Creo columnas default si no existen
    if not TableColumn.objects.count():
        init_columns()

    task.refresh_from_db()
    task.status = IndicatorsGenerationTask.FINISHED
    task.finished = timezone.now()
    task.save()


def save_network_indics(network_indics, indic_class, task):
    # Itero sobre los indicadores de red, creando modelos y agregándolos
    # a 'network_indicators'
    for indic_name, value in network_indics.items():
        indic_type = IndicatorType.objects.get_or_create(
            nombre=indic_name,
            tipo=indic_class)[0]
        network_indic = IndicadorRed(indicador_tipo=indic_type,
                                     indicador_valor=json.dumps(value))

        # Al ser los indicadores de red en cantidad reducida comparado con
        # la cantidad de los indicadores comunes, los guardo
        # uno por uno sin mayor impacto de performance
        network_indic.save()

    IndicatorsGenerationTask.info(task, u'Calculados {} indicadores de red'.format(len(network_indics)))


def save_indicators(indics_list, names, task):
    """Crea modelos de Django a partir de cada indicador, y los guarda.
    Los nombres de los catálogos son leídos a partir de una lista 'names',
    con los indicadores y los nombres ordenados de la misma manera"""

    indic_models = 0  # Lista con todos los indicadores generados
    for indicators in indics_list:
        catalog_name = names[indics_list.index(indicators)]
        if not catalog_name:  # Fallback en caso de catálogos muy erróneos
            catalog_name = "Catálogo sin nombre"

        # Itero sobre los indicadores calculados, creando modelos y
        # agregándolos a la lista 'indicators'
        for indic_name, value in indicators.items():

            indic_type = IndicatorType.objects.get_or_create(
                nombre=indic_name,
                tipo='RED')[0]
            indic = Indicador(jurisdiccion_nombre=catalog_name,
                              indicador_tipo=indic_type,
                              indicador_valor=json.dumps(value))
            indic_models += 1
            try:
                indic.save()
            except DataError:
                IndicatorsGenerationTask.info(task, u"Error guardando indicador: {0} - {1}: {2}"
                                              .format(catalog_name, indic_type, json.dumps(value)))

    IndicatorsGenerationTask.info(task, u'Calculados {0} indicadores en {1} catálogos'
                                  .format(indic_models, len(indics_list)))


def init_columns():
    """ Inicializa las columnas de las tablas de indicadores a partir de
    valores predeterminados en la configuración de la aplicación
    """
    for indicator_name in settings.DEFAULT_INDICATORS:
        indicator = IndicatorType.objects.get(nombre=indicator_name)
        column = TableColumn(indicator=indicator)
        column.clean()  # Setea el nombre default
        column.save()
