# Generated by Django 3.2 on 2021-04-17 21:51

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import main.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
                ('map_url', models.CharField(help_text='Карта площадки', max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AreaType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
                ('short_name', models.CharField(help_text='Короткое наименование', max_length=100)),
                ('full_name', models.CharField(help_text='Полное наименование', max_length=250)),
                ('code', models.PositiveBigIntegerField(default=0, help_text='Код ЦФО')),
                ('root_dir', models.CharField(help_text='Каталог со статикой', max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
                ('area', models.ForeignKey(blank=True, default=None, help_text='Родительская площадка', null=True, on_delete=django.db.models.deletion.CASCADE, to='main.area')),
                ('type', models.ForeignKey(blank=True, default=None, help_text='Тип ресурса', null=True, on_delete=django.db.models.deletion.CASCADE, to='main.resourcetype')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Время создания')),
                ('created_by', models.CharField(default='', help_text='Кем создано', max_length=50)),
                ('message', models.CharField(help_text='Сообщение', max_length=500)),
                ('active', models.BooleanField(blank=True, default=True)),
                ('resource', models.ForeignKey(blank=True, default=None, help_text='Объект запроса', null=True, on_delete=django.db.models.deletion.CASCADE, to='main.resource')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
                ('type', models.CharField(choices=[('bool', 'Булево'), ('real', 'Число'), ('text', 'Строка')], help_text='Тип поля', max_length=4)),
                ('value_bool', models.BooleanField(blank=True, default=False)),
                ('value_real', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('value_text', models.CharField(blank=True, max_length=250, null=True)),
                ('resource', models.ForeignKey(blank=True, default=None, help_text='Родительский ресурс', null=True, on_delete=django.db.models.deletion.CASCADE, to='main.resource')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
                ('message', models.CharField(help_text='Сообщение', max_length=500)),
                ('start', models.DateTimeField(blank=True, help_text='Начало брони')),
                ('finish', models.DateTimeField(blank=True, help_text='Окончание брони')),
                ('active', models.BooleanField(blank=True, default=True)),
                ('users_group', models.ForeignKey(blank=True, default=None, help_text='Группа', null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExtUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.user')),
                ('middle_name', models.CharField(help_text='Отчество', max_length=500)),
                ('active', models.BooleanField(blank=True, default=True)),
                ('company', models.ForeignKey(blank=True, default=None, help_text='Компания', null=True, on_delete=django.db.models.deletion.CASCADE, to='main.company')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
                ('description', models.CharField(help_text='Описание', max_length=500)),
                ('users', models.ManyToManyField(blank=True, default=None, help_text='Участники', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Наименование', max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Время создания')),
                ('created_by', models.CharField(default='', help_text='Кем создано', max_length=50)),
                ('changed_at', models.DateTimeField(auto_now=True, help_text='Время изменения')),
                ('changed_by', models.CharField(default='', help_text='Кем изменено', max_length=50)),
                ('start', models.DateTimeField(blank=True, help_text='Начало брони')),
                ('finish', models.DateTimeField(blank=True, help_text='Окончание брони')),
                ('confirmed', models.BooleanField(blank=True, default=False)),
                ('confirmed_at', models.DateTimeField(help_text='Время изменения')),
                ('confirmed_by', models.CharField(default='', help_text='Кем подтверждено', max_length=50)),
                ('confirmation_pin', models.PositiveSmallIntegerField(default=main.utils.get_pin, help_text='PIN-код')),
                ('active', models.BooleanField(blank=True, default=True)),
                ('event', models.ForeignKey(blank=True, default=None, help_text='Событие', null=True, on_delete=django.db.models.deletion.CASCADE, to='main.event')),
                ('resource', models.ForeignKey(blank=True, default=None, help_text='Объект бронирования', null=True, on_delete=django.db.models.deletion.CASCADE, to='main.resource')),
                ('user', models.ForeignKey(blank=True, default=None, help_text='Бронирующий', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='area',
            name='company',
            field=models.ForeignKey(blank=True, default=None, help_text='Компания', null=True, on_delete=django.db.models.deletion.CASCADE, to='main.company'),
        ),
        migrations.AddField(
            model_name='area',
            name='type',
            field=models.ForeignKey(blank=True, default=None, help_text='Тип площадки', null=True, on_delete=django.db.models.deletion.CASCADE, to='main.areatype'),
        ),
    ]
