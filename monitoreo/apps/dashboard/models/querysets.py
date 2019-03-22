# coding=utf-8
from __future__ import unicode_literals

import json
from collections import OrderedDict
from django.db import models


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
            value = json.loads(indicator.indicador_valor)
            if isinstance(value, (float, int)):
                numerical.setdefault(indicator.fecha, {})\
                    .update({indicator.indicador_tipo.nombre: value})

        return numerical