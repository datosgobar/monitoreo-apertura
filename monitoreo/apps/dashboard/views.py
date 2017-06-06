# coding=utf-8
from datetime import date, timedelta
from django.shortcuts import render
from .models import IndicadorRed


def landing(request):
    indicators = IndicadorRed.objects.filter(fecha=date.today())

    # Si todavía no se calcularon los indicadores de hoy (12 AM - 5 AM) usamos
    # los de ayer
    if not indicators:
        yesterday = date.today() - timedelta(days=1)
        indicators = IndicadorRed.objects.filter(fecha=yesterday)

    ok_pct = indicators.get(
        indicador_nombre="datasets_meta_ok_pct").indicador_valor

    actualizados_pct = indicators.get(
        indicador_nombre="datasets_actualizados_pct").indicador_valor

    context = {
        'ok_pct': ok_pct,
        'actualizados_pct': actualizados_pct
    }
    return render(request, 'dashboard/landing.html', context)
