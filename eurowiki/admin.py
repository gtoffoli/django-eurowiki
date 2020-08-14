"""
Defines admin options for the eurowiki app.
"""
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget

from . import models


@admin.register(models.StatementExtension)
class StatementExtensionAdmin(admin.ModelAdmin):
    """
    Admin module for statement extensions.
    """
    list_display = ['id', 'deleted', 'comment_enabled', 'uri_statement', 'literal_statement', ]

