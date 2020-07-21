# from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django import forms
from django.utils.translation import get_language, ugettext_lazy as _
from rdflib_django.models import NamedGraph, URIStatement, LiteralStatement


STATEMENT_CLASS_CHOICES = (('literal', _('Literal Statement')), ('uri', _('URI Statement')))
PREDICATE_CHOICES = settings.ORDERED_PREDICATE_KEYS
DATATYPE_CHOICES = (
    ('string', _('string')),
    ('integer',  _('integer')),
    ('date',  _('date')),
    ('gYear', _('year')),
    ('gMonthDay',  _('day of year')),
)
LANGUAGE_CHOICES = settings.EURO_LANGUAGES
language = get_language()[:2]
PREDICATE_CHOICES = [(key, settings.PREDICATE_LABELS[key].get(language, key)) for key in settings.ORDERED_PREDICATE_KEYS]
LITERAL_PREDICATE_CHOICES = [p for p in PREDICATE_CHOICES if p[0] in settings.LITERAL_PROPERTIES]
URI_PREDICATE_CHOICES = [p for p in PREDICATE_CHOICES if not p[0] in settings.LITERAL_PROPERTIES]
COUNTRY_PREDICATE_CHOICES = [p for p in URI_PREDICATE_CHOICES if p[0] in settings.EW_TREE_KEYS]
ITEM_PREDICATE_CHOICES = [p for p in URI_PREDICATE_CHOICES if not p[0] in settings.EW_TREE_KEYS]
OBJECT_TYPE_CHOICES = (
    ('old', _('existing graph node')),
    ('new',  _('new graph node')),
    ('ext',  _('linked external node')),
)
CONTEXT_CHOICES = []
for identifier in NamedGraph.objects.all().values_list('identifier', flat=True).distinct():
    context = identifier.n3().replace('<','').replace('>','')
    CONTEXT_CHOICES.append((context, context))

class StatementForm(forms.Form):
    subject = forms.CharField(required=True, label=_('subject'))
    statement_class = forms.ChoiceField(required=True, choices=STATEMENT_CLASS_CHOICES, label=_('statement class'), widget=forms.Select(attrs={'class':'form-control', 'onchange':'javascript:this.form.submit()'}))
    predicate = forms.ChoiceField(required=True, choices=PREDICATE_CHOICES, label=_('predicate'), widget=forms.Select(attrs={'class':'form-control',}))
    object_node_type = forms.ChoiceField(required=False, choices=OBJECT_TYPE_CHOICES, label=_('object node type'), widget=forms.Select(attrs={'class':'form-control', 'onchange':'javascript:this.form.submit()'}))
    object = forms.CharField(required=False, label=_('object node'))
    datatype = forms.ChoiceField(required=False, choices=DATATYPE_CHOICES, label=_('data type'), widget=forms.Select(attrs={'class':'form-control', 'onchange':'javascript:this.form.submit()'}))
    literal = forms.CharField(required=False, label=_('literal value'), widget=forms.Textarea(attrs={'rows': 4}))
    language = forms.ChoiceField(required=False, choices=LANGUAGE_CHOICES, label=_('string language'), widget=forms.Select(attrs={'class':'form-control',}))
    context = forms.ChoiceField(required=False, choices=CONTEXT_CHOICES, label=_('context'), widget=forms.Select(attrs={'class':'form-control',}))
