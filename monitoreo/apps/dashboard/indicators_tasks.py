# coding=utf-8
from __future__ import unicode_literals

import json
from urllib.parse import urljoin
from django.conf import settings
from django.utils import timezone
from django.db.utils import DataError
from django_rq import job

from pydatajson.core import DataJson
from django_datajsonar.models import Node

from monitoreo.apps.dashboard.series_csv_generators import IndicatorSeriesCSVGenerator
from monitoreo.apps.dashboard.enqueue_job import enqueue_job_with_timeout
from monitoreo.apps.dashboard.indicator_csv_zip_generator import IndicatorCSVZipGenerator
from monitoreo.apps.dashboard.models.tasks import TasksConfig
from .models import IndicatorsGenerationTask, TableColumn, IndicatorType, Indicador, IndicadorFederador,\
    IndicadorRed, HarvestingNode, CentralNode
from .helpers import load_catalogs

URL = "https://raw.githubusercontent.com/datosgobar/libreria-catalogos/master/"
CENTRAL = URL + 'datosgobar/data.json'


@job('indicators')
def indicators_run(_node=None):
    # El framework de tareas de django_datajsonar pasa para todos los casos un
    # nodo por parámetro. Esta tarea no hace uso de ese parámtro por el
    # momento
    task = IndicatorsGenerationTask.objects.create()
    timeout = TasksConfig.get_solo().indicators_timeout
    enqueue_job_with_timeout('indicators', generate_indicators, timeout, args=(task,))


@job('indicators', timeout=1800)
def generate_indicators(task):
    url_check_timeout = TasksConfig.get_solo().url_check_timeout
    data_json = DataJson(url_check_timeout=url_check_timeout)
    catalogs = load_catalogs(task, Node.objects.filter(indexable=True))
    validate_urls = TasksConfig.get_solo().indicators_url_check
    urls_check_threads = TasksConfig.get_solo().url_check_threads
    try:
        central_node = CentralNode.objects.get()
        central_catalog = urljoin(central_node.node.url, 'data.json')
    except (CentralNode.DoesNotExist, AttributeError):
        central_catalog = CENTRAL
    indics, network_indics = data_json.generate_catalogs_indicators(
        catalogs, central_catalog, identifier_search=True, broken_links=validate_urls,
        broken_links_threads=urls_check_threads)

    save_indicators(indics, task)
    save_network_indics(network_indics, 'RED', task)

    federator_catalogs = load_catalogs(
        task, HarvestingNode.objects.filter(enabled=True), harvesting=True)
    federator_indics, _ = data_json.generate_catalogs_indicators(
        federator_catalogs, identifier_search=True, broken_links=validate_urls,
        broken_links_threads=urls_check_threads)

    save_indicators(federator_indics, task, harvesting_nodes=True)
    # Creo columnas default si no existen
    if not TableColumn.objects.count():
        init_columns()

    write_time_series_files.delay()
    zip_indicators_csv.delay()

    task.refresh_from_db()
    task.status = IndicatorsGenerationTask.FINISHED
    task.finished = timezone.localtime()
    task.save()


def save_network_indics(network_indics, indic_class, task):
    # Itero sobre los indicadores de red, creando modelos y agregándolos
    # a 'network_indicators'
    for indic_name, value in network_indics.items():
        indic_type = IndicatorType.objects.get_or_create(
            nombre=indic_name,
            tipo=indic_class)[0]
        IndicadorRed.objects.update_or_create(fecha=timezone.localtime().date(),
                                              indicador_tipo=indic_type,
                                              defaults={'indicador_valor': json.dumps(value)})

    IndicatorsGenerationTask.info(task, 'Calculados {} indicadores de red'.format(len(network_indics)))


def save_indicators(indics_list, task, harvesting_nodes=False):
    """Crea modelos de Django a partir de cada indicador, y los guarda.
    Los nombres de los catálogos son leídos a partir de una lista 'names',
    con los indicadores y los nombres ordenados de la misma manera"""
    if harvesting_nodes:
        model = IndicadorFederador
    else:
        model = Indicador

    indic_models = 0  # Lista con todos los indicadores generados
    for indics in indics_list:
        indicators = indics.copy()
        catalog_name = indicators.pop('title')
        catalog_id = indicators.pop('identifier')
        # Itero sobre los indicadores calculados, creando modelos y
        # agregándolos a la lista 'indicators'
        for indic_name, value in indicators.items():
            indic_type = IndicatorType.objects.get_or_create(
                nombre=indic_name,
                tipo='RED')[0]

            try:
                model.objects.update_or_create(
                    fecha=timezone.localtime().date(),
                    jurisdiccion_nombre=catalog_name,
                    jurisdiccion_id=catalog_id,
                    indicador_tipo=indic_type,
                    defaults={'indicador_valor': json.dumps(value)})

                indic_models += 1
            except DataError:
                IndicatorsGenerationTask.info(
                    task, "Error guardando indicador: {0} - {1}: {2}"
                    .format(catalog_name, indic_type, json.dumps(value)))

    msg = 'Calculados {0} indicadores en {1} catálogos'\
        .format(indic_models, len(indics_list))
    if harvesting_nodes:
        msg += ' federadores'
    IndicatorsGenerationTask.info(task, msg)


def init_columns():
    """ Inicializa las columnas de las tablas de indicadores a partir de
    valores predeterminados en la configuración de la aplicación
    """
    for indicator_name in settings.DEFAULT_INDICATORS:
        indicator = IndicatorType.objects.get(nombre=indicator_name)
        column = TableColumn(indicator=indicator)
        column.clean()  # Setea el nombre default
        column.save()


@job('indicators', timeout=1800)
def write_time_series_files():
    generator = IndicatorSeriesCSVGenerator()
    generator.generate_network_time_series_files()
    generator.generate_nodes_time_series_files()
    generator.generate_federator_nodes_time_series_files()


@job('indicators', timeout=1800)
def zip_indicators_csv():
    generator = IndicatorCSVZipGenerator()
    generator.generate_network_panel_zip()
    generator.generate_node_panel_zip()
    generator.generate_federator_node_panel_zip()
