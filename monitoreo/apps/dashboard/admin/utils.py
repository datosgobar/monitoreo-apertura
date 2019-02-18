# coding=utf-8


def switch(updates):
    return lambda _, __, queryset: queryset.update(**updates)
