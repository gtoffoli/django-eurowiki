# from django.utils.translation import ugettext_lazy as _
from django import forms
from rdflib_django.models import  NamedGraph, NamespaceModel, URIStatement, LiteralStatement # Store, 


class NamedGraphForm(forms.ModelForm):
    class Meta:
        model = NamedGraph
        exclude = ()

class NamespaceModelForm(forms.ModelForm):
    class Meta:
        model = NamespaceModel
        exclude = ()

class LiteralStatementForm(forms.ModelForm):
    class Meta:
        model = LiteralStatement
        exclude = ()

class URIStatementForm(forms.ModelForm):
    class Meta:
        model = URIStatement
        exclude = ()

