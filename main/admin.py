from django.contrib import admin

# Register your models here.
from main.models import *

admin.site.register(Area)
admin.site.register(AreaType)
admin.site.register(ResourceType)
admin.site.register(Property)
admin.site.register(Resource)
admin.site.register(Company)
admin.site.register(Request)
admin.site.register(Notification)
admin.site.register(ExtUser)
admin.site.register(Event)
admin.site.register(Booking)
