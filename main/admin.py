from django.contrib import admin

# Register your models here.
from main.models.core import *

admin.site.register(Area)
admin.site.register(Resource)
admin.site.register(Company)
admin.site.register(Task)
admin.site.register(Notification)
admin.site.register(ExtUser)
admin.site.register(Event)
admin.site.register(Booking)
