from django.core.management.base import BaseCommand
from main.models.core import *
from django.db import connection


class Command(BaseCommand):
    help = "Destructively resets the database and installs some demonstration data."
    args = ""
    requires_system_checks = True


    def handle(self, *args, **options):
        self.clear_data()
        self.reset_sequences()

    def clear_data(self):
        self.delete_all_links()
        self.delete_all(Company)
        self.delete_all(Area)
        self.delete_all(Resource)
        self.delete_all(Group)
        self.delete_all(User)
        self.delete_all(ExtUser)
        self.delete_all(Event)
        self.delete_all(ServiceRequest)
        print('DB cleaned up successfully')

    def reset_sequences(self):
        print('Begin to reset all main sequences')
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT c.relname FROM pg_class c WHERE c.relkind = 'S' and c.relname like 'main%'
                union
                SELECT c.relname FROM pg_class c WHERE c.relkind = 'S' and c.relname = 'auth_user_id_seq';
            ''')
            rows = cursor.fetchall()
            for row in rows:
                print('\tReset sequence %s' % row[0])
                cursor.execute('ALTER SEQUENCE %s RESTART WITH 1' % row[0])
        print('Reset sequences successfully')


    def delete_all_links(self):
        print('Deleting all links')
        with connection.cursor() as cursor:
            cursor.execute('''
                delete FROM public.main_event_users;
            ''')
        print('Deleting links successfully')
        return True


    def delete_all(self, cls):
        print('Delete all %s' % cls.__name__)
        if hasattr(cls, "native_objects"):
            for item in cls.native_objects.all():
                item.native_delete()
        else:
            for item in cls.objects.all():
                item.delete()

