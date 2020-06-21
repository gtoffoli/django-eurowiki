# from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django import forms
from django.utils.translation import get_language, ugettext_lazy as _
from rdflib_django.models import URIStatement, LiteralStatement


class LiteralStatementForm(forms.ModelForm):
    class Meta:
        model = LiteralStatement
        exclude = ()

class URIStatementForm(forms.ModelForm):
    class Meta:
        model = URIStatement
        exclude = ()

STATEMENT_CLASS_CHOICES = (('lit', _('Literal Statement')), ('uri', _('URI Statement')))
PREDICATE_CHOICES = settings.ORDERED_PREDICATE_KEYS
DATATYPE_CHOICES = (
    ('string', _('string')),
    ('integer',  _('integer')),
    ('date',  _('date')),
    ('gYear', _('year')),
    ('gMonthDay',  _('day of year')),
)
LANGUAGE_CHOICES = settings.LANGUAGES
language = get_language()[:2]
PREDICATE_CHOICES = [(key, settings.PREDICATE_LABELS[key].get(language, key)) for key in settings.ORDERED_PREDICATE_KEYS]

class StatementForm(forms.Form):
    subject = forms.CharField(required=True, label=_('subject'))
    statement_class = forms.ChoiceField(required=True, choices=STATEMENT_CLASS_CHOICES, label=_('statement class'), widget=forms.Select(attrs={'class':'form-control', 'onchange':'javascript:this.form.submit()'}))
    predicate = forms.ChoiceField(required=True, choices=PREDICATE_CHOICES, label=_('predicate'), widget=forms.Select(attrs={'class':'form-control',}))
    object = forms.CharField(required=False, label=_('object node'))
    literal = forms.CharField(required=False, label=_('literal value'))
    datatype = forms.ChoiceField(required=False, choices=DATATYPE_CHOICES, label=_('data type'), widget=forms.Select(attrs={'class':'form-control',}))
    language = forms.ChoiceField(required=False, choices=LANGUAGE_CHOICES, label=_('string language'), widget=forms.Select(attrs={'class':'form-control',}))
