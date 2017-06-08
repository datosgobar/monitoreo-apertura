from django.shortcuts import render
from monitoreo.apps.dashboard.models import Indicador


def red_nodos(request):
    return render(request, 'nodos/nodos.html')
