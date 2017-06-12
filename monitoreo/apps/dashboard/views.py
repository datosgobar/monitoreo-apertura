# coding=utf-8
from datetime import date, timedelta
from django.shortcuts import render
from .models import IndicadorRed


def landing(request):
    # Obtengo indicadores de la red de ayer
    today = date.today()
    indicators = IndicadorRed.objects.filter(fecha=today)

    # Si todavía no se calcularon los indicadores de hoy (12 AM - 5 AM) usamos
    # los de ayer
    if not indicators:
        yesterday = today - timedelta(days=1)
        indicators = IndicadorRed.objects.filter(fecha=yesterday)

    if not indicators:  # Error, no hay indicadores cargados
        return render(request, '500.html', status=500)

    # Valores para mocking, a ser calculados posteriormente
    documentados_pct = 60
    descargables_pct = 75
    items = 0
    jurisdicciones = 0

    # Agarro el primer valor que devuelve los filters. El QuerySet no debería
    # estar vacío nunca, puesto que los indicadores se calculan todos juntos
    catalogos_cant = indicators.filter(
        indicador_tipo__nombre="catalogos_cant")[0].indicador_valor

    datasets_cant = indicators.filter(
        indicador_tipo__nombre="datasets_cant")[0].indicador_valor

    ok_pct = indicators.filter(
        indicador_tipo__nombre="datasets_meta_ok_pct")[0].indicador_valor

    actualizados_pct = indicators.filter(
        indicador_tipo__nombre="datasets_actualizados_pct")[0].indicador_valor

    context = {
        'fecha': today,
        'items': items,
        'jurisdicciones': jurisdicciones,
        'catalogos': catalogos_cant,
        'datasets': datasets_cant,
        'documentados_pct': documentados_pct,
        'descargables_pct': descargables_pct,
        'ok_pct': ok_pct,
        'actualizados_pct': actualizados_pct
    }
    return render(request, 'dashboard/landing.html', context)
