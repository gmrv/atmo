# http://stackoverflow.com/questions/433162/can-i-access-constants-in-settings-py-from-templates-in-django

from django import template
from django.conf import settings

register = template.Library()

# settings value
# Для доступа к файлу конфигурации
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")
