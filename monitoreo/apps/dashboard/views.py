# coding=utf-8
from django.http import HttpResponse
from django.shortcuts import render


def landing(request):
    return render(request, 'dashboard/landing.html')
