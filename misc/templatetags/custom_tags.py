# -*- coding: utf-8 -*-

from django import template
register = template.Library()

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)

@register.filter
def index(indexable, i):
    return indexable[i]