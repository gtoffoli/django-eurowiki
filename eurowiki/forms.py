# from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django import forms
from django.utils.translation import get_language, ugettext_lazy as _
from rdflib_django.models import NamedGraph
from .models import SparqlQuery

STATEMENT_CLASS_CHOICES = (('literal', _('Literal Statement')), ('uri', _('URI Statement')))
PREDICATE_CHOICES = settings.ORDERED_PREDICATE_KEYS
DATATYPE_CHOICES = (
    ('string', _('string')),
    ('integer',  _('integer')),
    ('date',  _('date')),
    ('gYear', _('year')),
    ('gMonthDay',  _('day of year')),
)
# LANGUAGE_CHOICES = [[l, l] for l in settings.EURO_LANGUAGES_CODES[1:]]
LANGUAGE_CHOICES = settings.EURO_LANGUAGES[1:]
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
    predicate = forms.ChoiceField(required=True, choices=PREDICATE_CHOICES, label=_('predicate'), widget=forms.Select(attrs={'class':'form-control', 'onchange':'javascript:this.form.submit()'}))
    object_node_type = forms.ChoiceField(required=False, choices=OBJECT_TYPE_CHOICES, label=_('object type'), widget=forms.Select(attrs={'class':'form-control', 'onchange':'javascript:this.form.submit()'}))
    object = forms.CharField(required=False, label=_('object'))
    datatype = forms.ChoiceField(required=False, choices=DATATYPE_CHOICES, label=_('data type'), widget=forms.Select(attrs={'class':'form-control', 'onchange':'javascript:this.form.submit()'}))
    literal = forms.CharField(required=False, label=_('literal value'), widget=forms.Textarea(attrs={'rows': 4}))
    language = forms.ChoiceField(required=False, choices=LANGUAGE_CHOICES, label=_('string language'), widget=forms.Select(attrs={'class':'form-control',}))
    context = forms.ChoiceField(required=False, choices=CONTEXT_CHOICES, label=_('context'), widget=forms.Select(attrs={'class':'form-control',}))

class QueryForm(forms.ModelForm):
    class Meta:
        model = SparqlQuery
        fields = ['id', 'title', 'description', 'text',]

    id = forms.CharField(required=False, widget=forms.HiddenInput())
    title = forms.CharField(required=True, label=_('title'), widget=forms.TextInput(attrs={'class':'form-control',})) # help_text=_('please use a short title'))
    description = forms.CharField(required=True, label=_('short description'), widget=forms.Textarea(attrs={'class':'form-control', 'rows': 3, 'cols': 80,}))
    text = forms.CharField(required=True, label=_('SPARQL query text'), widget=forms.Textarea(attrs={'class':'form-control', 'rows': 6, 'cols': 80,}))


RUN_QUERY_CHOICES = (
    ('show', _('show results')),
    ('export', _('export results to CSV file')+' (**) '),
)

def apply_language_priorities(language_choices, languages):
    choices = []
    for code in languages:
        for choice in language_choices:
            if choice[0] == code:
                choices.append(choice)
    for choice in language_choices:
        if choice[0] not in languages:
            choices.append(choice)         
    return choices

class QueryExecForm(forms.Form):
    query = forms.IntegerField(widget=forms.HiddenInput())
    languages = forms.MultipleChoiceField(choices=LANGUAGE_CHOICES,
        label = _('languages'), required=False,
        help_text = _("set languages priority") + ' (*) ',
        widget = forms.SelectMultiple(attrs={'id':'select_languages', 'class':'form-control', 'size': 3, 'style': 'width: auto;',}))
    columns = forms.MultipleChoiceField(choices=[],
        label = _('columns'), required=False,
        help_text = _("select colums to display"),
        widget=forms.SelectMultiple(attrs={'class':'form-control', 'size': 3, 'style': 'width: auto;',}))
    output_mode = forms.ChoiceField(required=False, choices=RUN_QUERY_CHOICES,
        label=_('show/export results'),
        widget=forms.RadioSelect())
