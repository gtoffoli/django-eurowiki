# Generated by Django 2.1.3 on 2020-08-12 22:37

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rdflib_django', '0002_auto_20181112_1317'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatementExtension',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('deleted', models.BooleanField(default=False, verbose_name='deleted')),
                ('comment_enabled', models.BooleanField(default=True, help_text='Allows comments if checked.', verbose_name='comments enabled')),
                ('literal_statement', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='literal_statement', to='rdflib_django.LiteralStatement')),
                ('uri_statement', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uri_statement', to='rdflib_django.URIStatement')),
            ],
        ),
    ]
