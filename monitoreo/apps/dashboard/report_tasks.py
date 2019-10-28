# coding=utf-8
from __future__ import unicode_literals

from django_datajsonar.models import Node
from django_rq import job
from pydatajson.custom_exceptions import NonParseableCatalog
from requests.exceptions import RequestException

from monitoreo.apps.dashboard import models
from monitoreo.apps.dashboard.enqueue_job import enqueue_job_with_timeout
from monitoreo.apps.dashboard.models.tasks import TasksConfig
from monitoreo.apps.dashboard.report_generators import \
    ValidationReportGenerator, IndicatorReportGenerator, NewlyDatasetReportGenerator


@job('reports')
def send_reports(node=None):
    report_task = models.ReportGenerationTask.objects.create()
    indicators_run(report_task, node=node)


@job('reports')
def send_validations(node=None):
    validation_task = models.ValidationReportTask.objects.create()
    timeout = TasksConfig.get_solo().validation_timeout
    enqueue_job_with_timeout('reports', validation_run, timeout, args=(validation_task,), kwargs={'node': node})


@job('reports')
def send_newly_reports(_=None):
    newly_report_task = models.tasks.NewlyReportGenerationTask.objects.create()
    newly_report_run(newly_report_task)


@job('reports')
def indicators_run(report_task, node=None):
    try:
        indicators_task = models.IndicatorsGenerationTask.objects\
            .filter(status=models.IndicatorsGenerationTask.FINISHED)\
            .exclude(finished__isnull=True).latest('finished')
    except models.IndicatorsGenerationTask.DoesNotExist:
        # No hay un task cargado
        return

    generator = IndicatorReportGenerator(indicators_task, report_task)

    if node:
        mail = generator.generate_node_indicators_email(node)
        generator.send_email(mail)
        generator.close_task()
        return

    mail = generator.generate_network_indicators_email()
    generator.send_email(mail)

    central_node = models.CentralNode.get_solo().node
    if central_node:
        mail = generator.generate_federation_indicators_email(central_node)
        generator.send_email(mail)

    nodes = Node.objects.filter(indexable=True)
    for target_node in nodes:
        mail = generator.generate_node_indicators_email(target_node)
        generator.send_email(mail, target_node)

    generator.close_task()


@job('reports')
def validation_run(validation_task, node=None):
    generator = ValidationReportGenerator(validation_task)
    nodes = [node] if node else Node.objects.filter(indexable=True)
    for target_node in nodes:
        try:
            mail = generator.generate_email(node=target_node)
        except (NonParseableCatalog, RequestException) as e:
            msg = 'Error enviando la validación de {}: {}'\
                .format(target_node.catalog_id, str(e))
            models.ValidationReportTask.info(validation_task, msg)
            mail = generator.generate_error_mail(target_node, str(e))

        generator.send_email(mail, node=target_node)
    generator.close_task()


@job('reports')
def newly_report_run(newly_report_task):
    try:
        last_newly_report_date = models.tasks.NewlyReportGenerationTask.objects \
            .filter(status=models.tasks.NewlyReportGenerationTask.FINISHED) \
            .exclude(finished__isnull=True).latest('finished').finished
    except models.tasks.NewlyReportGenerationTask.DoesNotExist:
        # Si no hubo reportes previos, es decir, si este es el primer reporte, no enviamos nada
        newly_report_task.close_task()
        return
    generator = NewlyDatasetReportGenerator(newly_report_task, last_newly_report_date)

    new_datasets = generator.get_new_datasets()
    if not new_datasets:
        generator.close_task()
        return

    catalog_identifiers = [dataset.catalog.identifier for dataset in new_datasets]
    nodes_to_report = Node.objects.filter(catalog_id__in=catalog_identifiers)

    for node in nodes_to_report:
        mail = generator.generate_email(node)
        generator.send_email(mail, node)

    staff_mail = generator.generate_email()
    generator.send_email(staff_mail)

    generator.close_task()
