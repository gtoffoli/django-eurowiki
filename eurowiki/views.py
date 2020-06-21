# see https://stackoverflow.com/questions/2112715/how-do-i-fix-pydev-undefined-variable-from-import-errors (Eclipse)
# Window -> Preferences -> PyDev -> Editor -> Code Analysis -> Undefined -> Undefined Variable From Import -> Ignore
from rdflib.term import BNode
from rdflib_django.models import Store, NamedGraph, NamespaceModel, URIStatement, LiteralStatement

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django import forms
from django.utils.translation import get_language
from django.views import View
from django.contrib.auth.decorators import login_required
from django.conf import settings

from rdflib_django.models import URIStatement, LiteralStatement
from rdflib_django.utils import get_named_graph, get_conjunctive_graph

from .classes import Country, Item, Predicate
from .forms import URIStatementForm, LiteralStatementForm
from .forms import StatementForm
from .utils import make_uriref, id_from_uriref, friend_uri, friend_graph

def eu_countries(language=settings.LANGUAGE_CODE):
    return [Country(id=qcode) for qcode in settings.EU_COUNTRY_LABELS.keys()]

def homepage(request):
    return render(request, 'homepage.html')

def search(request):
    return render(request, 'search.html')

def list_stores(request):
    stores = Store.objects.all()
    return render(request, 'list_stores.html', {'stores': stores})

def list_named_graphs(request):
    named_graphs = NamedGraph.objects.all()
    return render(request, 'list_named_graphs.html', {'named_graphs': named_graphs})

def list_namespaces(request):
    namespaces = NamespaceModel.objects.all()
    return render(request, 'list_namespaces.html', {'namespaces': namespaces})

def list_uri_statements(request):
    lang = get_language()
    statements = URIStatement.objects.all().order_by('context', 'subject', 'predicate')
    statements = sorted(statements, key=lambda s: settings.ORDERED_PREDICATE_KEYS.index(id_from_uriref(s.predicate)))
    statement_dicts = [{'graph': friend_graph(s.context), 'subject': friend_uri(s.subject, lang=lang), 'predicate': friend_uri(s.predicate, lang=lang), 'object': friend_uri(s.object, lang=lang)}
                       for s in statements]
    return render(request, 'list_uri_statements.html', {'statement_dicts': statement_dicts})

def list_literal_statements(request):
    lang = get_language()
    statements = LiteralStatement.objects.all().order_by('context', 'subject', 'predicate')
    statement_dicts = [{'graph': friend_graph(s.context), 'subject': friend_uri(s.subject, lang=lang), 'predicate': friend_uri(s.predicate, lang=lang), 'object': str(s.object)}
                       for s in statements]
    return render(request, 'list_literal_statements.html', {'statement_dicts': statement_dicts})

def list_statements(request, graph_identifier=None):
    lang = get_language()
    if graph_identifier:
        graph = get_named_graph(graph_identifier)
    else:
        graph = get_conjunctive_graph()
    statement_dicts = [{'graph': 'wikidata', 'subject': friend_uri(s, lang=lang), 'predicate': friend_uri(p, lang=lang), 'object': friend_uri(o, lang=lang)}
                           for s, p, o in graph]
    return render(request, 'list_statements.html', {'statement_dicts': statement_dicts})
        
def view_uri_statement(request, statement_id):
    statement = get_object_or_404(URIStatement, pk=statement_id)
    return render(request, 'uri_statement.html', {'statement': statement})

@method_decorator(login_required, name='post')
class editURIStatement(View):
    form_class = URIStatementForm
    template_name = 'edit_uri_statement.html'

    def get(self, request, statement_id=None):
        if statement_id:
            statement = get_object_or_404(URIStatement, pk=statement_id) 
            form = self.form_class(instance=statement)
        else:
            initial = {}
            form = self.form_class(initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            statement = form.save()
            return HttpResponseRedirect('/uri_statement/{}/'.format(statement.id))
        return render(request, self.template_name, {'form': form})

def view_literal_statement(request, statement_id):
    statement = get_object_or_404(LiteralStatement, pk=statement_id)
    return render(request, 'literal_statement.html', {'statement': statement})

@method_decorator(login_required, name='post')
class editLiteralStatement(View):
    form_class = LiteralStatementForm
    template_name = 'edit_literal_statement.html'

    def get(self, request, statement_id=None):
        if statement_id:
            statement = get_object_or_404(URIStatement, pk=statement_id) 
            form = self.form_class(instance=statement)
        else:
            initial = {}
            form = self.form_class(initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            statement = form.save()
            return HttpResponseRedirect('/literal_statement/{}/'.format(statement.id))
        return render(request, self.template_name, {'form': form})

def view_country(request, item_code):
    assert item_code[0]=='Q'
    countries = []
    country = Country(id=item_code)
    countries.append(country)
    return render(request, 'country.html', {'countries_selected' : countries})

def view_countries(request):
    countries= []
    post=request.POST
    if post:
        countries_code = post.getlist('group',[])
        for country_code in countries_code:
            assert country_code[0]=='Q'
            country = Country(id=country_code)
            countries.append(country)
    return render(request, 'country.html', {'countries_selected' : countries})

def view_item(request, item_code):
    if len(item_code)==35:
        bnode = BNode(item_code)
        item = Item(bnode=bnode)
    else:
        item = Item(id=item_code)
    return render(request, 'item.html', {'item' : item})

def edit_item(request, item_code):
    if len(item_code)==35:
        bnode = BNode(item_code)
        item = Item(bnode=bnode)
    else:
        item = Item(id=item_code)
    return render(request, 'item_edit.html', {'item' : item})

# @method_decorator(login_required, name='post')

class editStatement(View):
    form_class = StatementForm
    template_name = 'edit_statement.html'

    def get(self, request, statement_id=None, subject_id=None):
        language = get_language()[:2]
        if statement_id:
            statement_class = 'lit' # estrarre dallo statement
            if statement_class=='uri':
                statement = get_object_or_404(URIStatement, pk=statement_id)
            else:
                statement = get_object_or_404(LiteralStatement, pk=statement_id)
            form = self.form_class(instance=statement)
        if subject_id:
            statement_class = 'lit'
            initial = { 'statement_class': 'lit', 'subject': subject_id, 'datatype': 'string', 'language': language }
        form = self.form_class(initial=initial)
        if subject_id:
            form.fields['object'].widget = forms.HiddenInput()
            # form.fields['datatype'].widget = forms.HiddenInput()
        return render(request, self.template_name, {'form':form, 'subject':subject_id, 'statement':statement_id})

    def post(self, request, statement_id=None, subject_id=None):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # statement = form.save()
            # return HttpResponseRedirect('/uri_statement/{}/'.format(statement.id))
        statement_class = data['statement_class']
        datatype = data['datatype']
        if statement_class=='lit':
            form.fields['object'].widget = forms.HiddenInput()
            if not datatype=='string':
                form.fields['language'].widget = forms.HiddenInput()
        else: # statement_class=='uri'
            form.fields['literal'].widget = forms.HiddenInput()
            form.fields['datatype'].widget = forms.HiddenInput()
            form.fields['language'].widget = forms.HiddenInput()      
        return render(request, self.template_name, {'form': form, 'subject':subject_id, 'statement':statement_id})
