from django.db import models
from django_datajsonar.models import Dataset


class DatasetPresentRecord(models.Model):

    class Meta:
        verbose_name_plural = "Campos de " \
                              "presentismo de Dataset"

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "Campo de presentismo de Dataset"
    dataset = models.OneToOneField(
        Dataset,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Dataset"
    )
    present_record = \
        models.BooleanField(default=False,
                            verbose_name="Presente en la última "
                                         "corrida de datasets "
                                         "no presentes")
