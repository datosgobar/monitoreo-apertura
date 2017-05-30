# coding=utf-8
from django.http import HttpResponse


def test(request):
    return HttpResponse("Landing page del dashboard de monitoreo.")

