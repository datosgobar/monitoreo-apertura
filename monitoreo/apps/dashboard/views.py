# coding=utf-8
from datetime import date, timedelta
from django.shortcuts import render
from .models import IndicadorRed


def landing(request):
    today = date.today()
    indicators = IndicadorRed.objects.filter(fecha=today)

    # Si todavía no se calcularon los indicadores de hoy (12 AM - 5 AM) usamos
    # los de ayer
    if not indicators:
        yesterday = today - timedelta(days=1)
        indicators = IndicadorRed.objects.filter(fecha=yesterday)

    catalogos_cant = indicators.get(
        indicador_nombre="catalogos_cant").indicador_valor

    datasets_cant = indicators.get(
        indicador_nombre="datasets_cant").indicador_valor

    items = 0
    jurisdicciones = 0

    ok_pct = indicators.get(
        indicador_nombre="datasets_meta_ok_pct").indicador_valor

    actualizados_pct = indicators.get(
        indicador_nombre="datasets_actualizados_pct").indicador_valor

    documentados_pct = 60
    descargables_pct = 75

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
