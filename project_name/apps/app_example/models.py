# coding=utf-8
from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=50)

    def short_title(self):
        return str(self.title)[:4]

    def __unicode__(self):
        return self.title
