from django.contrib.contenttypes.models import ContentType
from django import template

register = template.Library()

@register.filter
def viewtrack(value):
    ct = ContentType.objects.get_for_model(value)
    return 'add_view_for(%d,%d)' % (ct.pk, value.pk)
