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

def extuser_to_json(extuser, is_short=False):
    """
    Конвертим расширенного пользователя в json
    todo: пофиксить конвертинг через serializers.serialize('json', extuser)
    """
    if is_short:
        result = {
            "id": extuser.id,
            "username": extuser.username,
        }
    else:
        result = {
            "id": extuser.id,
            "username": extuser.username,
            "first_name": extuser.first_name,
            "middle_name": extuser.middle_name,
            "last_name": extuser.last_name,
            "email": extuser.email,
            "is_superuser": extuser.is_superuser,
            "is_staff": extuser.is_staff,
            "is_active": extuser.is_active,
            "company_id": extuser.company_id,
            "booking_set": []
        }

        booking_set = extuser.booking_set.all()
        booking_arr = []
        for b in booking_set:
            booking_arr.append({
                "id": b.id,
                "start_ts": b.start_ts,
                "end_ts": b.end_ts
            })
        result["booking_set"] = booking_arr
    return result
