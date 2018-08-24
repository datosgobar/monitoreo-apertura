# coding=utf-8
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from monitoreo.apps.dashboard.indicators_tasks import generate_indicators
from monitoreo.apps.dashboard.models import IndicatorsGenerationTask


class Command(BaseCommand):
    help = """Calcula indicadores de la red de nodos del PAD de la república
    Argentina. Los catálogos son automáticamente leído de su librería remota,
    con raíz en https://www.github.com/datosgobar/libreria-catalogos"""

    def handle(self, *args, **options):
        # Llama sincrónicamente
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task)
