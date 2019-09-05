# coding=utf-8
from __future__ import unicode_literals

from tempfile import NamedTemporaryFile

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django_datajsonar.models import Dataset, Node, Catalog
from pydatajson.core import DataJson

from monitoreo.apps.dashboard.email_renderer import ReportSender, EmailRenderer
from . import models


class AbstractReportGenerator:
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, report_task, renderer):
        self.report_task = report_task
        self.sender = ReportSender(report_task)
        self.renderer = renderer

    def close_task(self):
        self.sender.close_connection()
        self.report_task.refresh_from_db()
        self.report_task.status = self.report_task.FINISHED
        self.report_task.finished = timezone.now()
        self.report_task.save()

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    def send_email(self, mail, node=None):
        self.sender.send_email(mail, node=node)

    def render_templates(self, context):
        return self.renderer.render_templates(context)

    def render_error_templates(self, context):
        return self.renderer.render_error_templates(context)


class IndicatorReportGenerator(AbstractReportGenerator):

    def __init__(self, indicators_task, report_task):
        self.indicators_task = indicators_task
        renderer = EmailRenderer('reports', 'indicators.txt', 'indicators.html')
        super(IndicatorReportGenerator, self).__init__(report_task, renderer)

    def _generate_email(self, context):
        """Genera y manda el mail con el reporte de indexación. Si node es
        especificado, genera el reporte con valores de entidades pertenecientes
        únicamente a ese nodo (reporte individual). Caso contrario (default),
        genera el reporte de indexación global
        """

        start_time = self._format_date(self.indicators_task.created)
        subject = u'[{}] Indicadores Monitoreo Apertura ({}): {}'\
            .format(settings.ENV_TYPE, context['target'], start_time)
        mail = self.render_templates(context)
        mail.subject = subject

        listed = context['listed']
        for indicator in listed:
            if listed[indicator]:
                body = render_to_string(
                    'reports/datasets.csv',
                    context={'dataset_list': listed[indicator]})
                mail.attach('{}.csv'.format(indicator), body, 'text/csv')
        return mail

    def generate_network_indicators_email(self):
        context = {
            'finish_time': self._format_date(self.indicators_task.finished),
            'target': 'Red'
        }

        context.update(
            self._get_summary_and_details_indicators(models.IndicadorRed)
        )
        context['logs'] = self.indicators_task.logs
        mail = self._generate_email(context)
        mail.attach('info.log', self.indicators_task.logs, 'text/plain')
        return mail

    def generate_federation_indicators_email(self, node):
        context = {
            'finish_time': self._format_date(self.indicators_task.finished),
            'target': node.catalog_id
        }

        context.update(
            self._get_summary_and_details_indicators(models.IndicadorFederador)
        )
        context['logs'] = self.indicators_task.logs

        mail = self._generate_email(context)
        return mail

    def generate_node_indicators_email(self, node):
        context = {
            'finish_time': self._format_date(self.indicators_task.finished),
            'target': node.catalog_id,
        }
        context.update(
            self._get_summary_and_details_indicators(models.Indicador, node)
        )
        mail = self._generate_email(context)
        return mail

    def _get_current_indicators(self, queryset, node=None):
        return queryset.sorted_indicators_on_date(
            self.indicators_task.finished.astimezone(
                timezone.get_current_timezone()).date(),
            node)

    def _get_summary_and_details_indicators(self, model, node=None):
        result = {}
        queryset = model.objects.filter(indicador_tipo__resumen=True)
        result['one_d_summary'], result['multi_d_summary'], _ = \
            self._get_current_indicators(queryset, node=node)

        queryset = model.objects.filter(indicador_tipo__mostrar=True)
        result['one_dimensional_indics'], \
            result['multi_dimensional_indics'], \
            result['listed'] = self._get_current_indicators(queryset, node=node)
        return result


class ValidationReportGenerator(AbstractReportGenerator):
    def __init__(self, report_task):
        self.report_task = report_task
        renderer = EmailRenderer('reports', 'validation.txt', 'validation.html',
                                 error_dir='errors')
        super(ValidationReportGenerator, self).__init__(report_task, renderer)

    def generate_email(self, node=None):
        if not node:
            # No genera mail de staff
            return None
        catalog = DataJson(node.catalog_url, catalog_format=node.catalog_format)
        validation = catalog.validate_catalog(only_errors=True)
        validation_time = self._format_date(timezone.now())
        if validation['status'] == 'OK':
            msg = "Catálogo {} válido.".format(node.catalog_id)
            self.report_task.info(self.report_task, msg)
            return None
        context = {
            'validation_time': validation_time,
            'status': validation['status'],
            'catalog': validation['error']['catalog'],
            'dataset_list': validation['error']['dataset']
        }

        mail = self.render_templates(context)
        subject = u'[{}] Validacion de catálogo {}: {}'.format(
            settings.ENV_TYPE, node.catalog_id, validation_time)
        mail.subject = subject

        with NamedTemporaryFile(suffix='.xlsx') as tmpfile:
            catalog.validate_catalog(export_path=tmpfile.name)
            mail.attach('reporte_validacion_{}.xlsx'.format(node.catalog_id),
                        tmpfile.read())

        return mail

    def generate_error_mail(self, node, error):
        context = {'error': error}
        validation_time = self._format_date(timezone.now())
        mail = self.render_error_templates(context)
        subject = u'[{}] Error validando catálogo {}: {}'.format(
            settings.ENV_TYPE, node.catalog_id, validation_time)
        mail.subject = subject
        return mail

    def send_email(self, mail, node=None):
        # Si mail es None, la validación no encontró errores.
        # No hay nada que mandar
        if mail is not None:
            super(ValidationReportGenerator, self).send_email(mail, node=node)


class NewlyDatasetReportGenerator(AbstractReportGenerator):
    def __init__(self, report_task, last_newly_report_date):
        self.report_task = report_task
        self.last_report_date = last_newly_report_date
        self.new_datasets = Dataset.objects.filter(time_created__gt=self.last_report_date)
        renderer = EmailRenderer('reports', 'newly.txt', 'newly.html')
        super(NewlyDatasetReportGenerator, self).__init__(report_task, renderer)

    def get_new_datasets(self):
        return self.new_datasets

    def generate_email(self, node=None):
        report_date = timezone.now().date()
        if not node:
            subject = f'[monitoreo-apertura] Reporte de novedades del {report_date}'
            nodes_list = self._create_node_and_new_datasets_pairs(self.new_datasets)
            context = {'nodes_list': nodes_list}
        else:
            subject = f'[monitoreo-apertura] Reporte de novedades para {node} del {report_date}'
            datasets_list = self._get_new_datasets_for_node(node, self.new_datasets)
            context = {
                'node': node,
                'datasets_list': datasets_list
            }
        mail = self.render_templates(context)
        mail.subject = subject
        return mail

    def _get_new_datasets_for_node(self, node, all_new_datasets):
        catalog = Catalog.objects.get(identifier=node.catalog_id)
        new_datasets_in_node = [dataset for dataset in catalog.dataset_set.all()
                                if dataset in all_new_datasets]
        return new_datasets_in_node

    def _create_node_and_new_datasets_pairs(self, all_new_datasets):
        nodes_and_datasets_pairs = []
        catalog_identifiers = [dataset.catalog.identifier for dataset in all_new_datasets]
        nodes_to_report = Node.objects.filter(catalog_id__in=catalog_identifiers)

        for node in nodes_to_report:
            new_datasets_in_node = self._get_new_datasets_for_node(node, all_new_datasets)
            nodes_and_datasets_pairs.append((node, new_datasets_in_node))

        return nodes_and_datasets_pairs
