'''
Created on 08/lug/2014
@author: giovanni
'''

from django.utils import translation
from django.utils.translation import activate
from django.conf import settings

from haystack import indexes
from haystack.fields import EdgeNgramField

from commons.utils import strings_from_html

"""

# vedi https://github.com/toastdriven/django-haystack/issues/609

from django.contrib.flatpages.models import FlatPage
def flatpage_indexable_text(self):
    strings = strings_from_html(self.content, fragment=True)
    return ' '.join(strings)
FlatPage.indexable_text = flatpage_indexable_text

class FlatPageIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.EdgeNgramField(document=True, use_template=True)
    name = indexes.CharField(model_attr='title', indexed=False)
    slug = indexes.CharField(model_attr='url', indexed=False)

    def get_model(self):
        activate('en')
        return FlatPage

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(url__icontains='help')
"""

from rdflib_django.models import LiteralStatement

class LiteralStatementIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.EdgeNgramField(document=True, use_template=True)
    item_code = indexes.CharField(indexed=False, use_template=True)
    is_country = indexes.CharField(indexed=False, use_template=True)

    def get_model(self):
        activate('en')
        return LiteralStatement

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(predicate__icontains='label')


from django.utils.translation import ugettext_lazy as _
from django import forms
from haystack.forms import ModelSearchForm, model_choices
class eurowikiModelSearchForm(ModelSearchForm):
    def __init__(self, *args, **kwargs):
        super(ModelSearchForm, self).__init__(*args, **kwargs)
        self.fields['models'] = forms.MultipleChoiceField(choices=model_choices(), required=False, label=_('In'), widget=forms.CheckboxSelectMultiple)

from collections import defaultdict
from django.shortcuts import render

q_extra = ['(', ')', '[', ']', '"']
def clean_q(q):
    for c in q_extra:
        q = q.replace(c, '')
    return q

def navigation_autocomplete(request, template_name='autocomplete.html'):
    q = request.GET.get('q', '')
    q = clean_q(q)
    context = {'q': q}

    if settings.USE_HAYSTACK:
        from haystack.query import SearchQuerySet
        MAX = 16
        results = SearchQuerySet().filter(text=q)
        if results.count() > MAX:
            results = results[:MAX]
            context['more'] = True
        queries = defaultdict(list)
        for result in results:
            klass = result.model.__name__
            values_list = [result.get_stored_fields()['text'], result.get_stored_fields()['item_code'], result.get_stored_fields()['is_country']]
            queries[klass].append(values_list)
    context.update(queries)
    return render(request, template_name, context)
