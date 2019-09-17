# coding=utf-8
from __future__ import unicode_literals

import json
import logging
from collections import OrderedDict

from django.db import models

LOGGER = logging.getLogger(__name__)


class IndicatorQuerySet(models.QuerySet):

    def sorted_indicators_on_date(self, date, node=None):
        indicators = self.filter(fecha=date)
        if node:
            indicators = indicators.filter(jurisdiccion_id=node.catalog_id)
        indicators = indicators.order_by('indicador_tipo__order')

        one_dimensional = OrderedDict()
        multi_dimensional = OrderedDict()
        listed = OrderedDict()
        for indicator in indicators:
            value = json.loads(indicator.indicador_valor)
            if isinstance(value, dict):
                value = OrderedDict(sorted(value.items(), key=lambda t: t[1],
                                           reverse=True))
                multi_dimensional[indicator.indicador_tipo.nombre] = value
            elif isinstance(value, list):
                listed[indicator.indicador_tipo.nombre] = value
            else:
                one_dimensional[indicator.indicador_tipo.nombre] = value

        return one_dimensional, multi_dimensional, listed

    def numerical_indicators_by_date(self, node_id=None):
        indicators = self.order_by('fecha')
        if node_id:
            indicators = indicators.filter(jurisdiccion_id=node_id)

        numerical = OrderedDict()
        for indicator in indicators:
            try:
                value = json.loads(indicator.indicador_valor)
                if isinstance(value, (float, int)):
                    numerical.setdefault(indicator.fecha, {})\
                        .update({indicator.indicador_tipo.nombre: value})
            except json.JSONDecodeError:
                msg = f'error parseando el indicador:{indicator.pk}'
                LOGGER.warning(msg)
        return numerical

    def csv_panel_indicators(self):
        lookup_field = self.model.CSV_PANEL_FIELD
        indicators = self.filter(**{'indicador_tipo__' + lookup_field: True})
        indicators = indicators.order_by('fecha')
        return indicators
