from datetime import datetime
from django.utils import timezone

def get_response_template(code='0', result={}, source='unknown') -> object:
    template = {
        'code': code,
        'result': result,
        'source': source
    }
    return template

def datetimestring_to_ts(datetimestring, template):
    return timezone.make_aware(
        datetime.strptime(datetimestring, template),
        timezone.get_current_timezone()
    )