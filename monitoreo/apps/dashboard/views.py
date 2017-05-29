# coding=utf-8
from django.http import HttpResponse


def test(request):
    return HttpResponse("hola")
