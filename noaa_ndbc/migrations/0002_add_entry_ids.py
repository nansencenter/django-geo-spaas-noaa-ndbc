# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-20 13:27
from __future__ import unicode_literals

from django.db import migrations

def set_entry_id(apps, schema_editor):
    model = apps.get_model('catalog', 'dataset')
    for row in model.objects.filter(source__instrument__short_name='WIND MONITOR'):
        uri = row.dataseturi_set.all()[0].uri
        ds = netCDF4.Dataset(uri)
        row.entry_id = 'NOAA_NDBC_%s'%ds.station
        row.save()

class Migration(migrations.Migration):

    dependencies = [
        ('noaa_ndbc', '0001_initial'),
        ('catalog', '0005_remove_entry_id_null'),
    ]

    operations = [
        migrations.RunPython(set_entry_id, reverse_code=migrations.RunPython.noop),
    ]