# coding=utf-8
from __future__ import unicode_literals
from django.contrib import admin

from . import indicator_types, indicators, nodes, tasks

admin.site.login_template = 'admin/login.html'
