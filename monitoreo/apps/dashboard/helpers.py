#! coding: utf-8
from django.db.models import QuerySet


def fetch_latest_indicadors(indicators):
    """A partir de un QuerySet de todos los indicadores, devuelve un conjunto
    con todos los últimos (más recientes) indicadores de cada tipo.
    
    args:
        indicators (QuerySet): QuerySet con todos los modelos a ordenar por
            su campo 'fecha' (de tipo DateTimeField)
    returns:
        dict: conjunto iterable de python con todos los indicadores más 
        recientes como valores, y los nombres como claves
    """
    indicators = indicators.order_by('-fecha')
    latest = {}
    for i in indicators:
        if i.indicador_tipo.nombre not in latest:
            latest[i.indicador_tipo.nombre] = i.indicador_valor
    return latest
