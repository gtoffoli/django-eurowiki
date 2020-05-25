# see https://stackoverflow.com/questions/2112715/how-do-i-fix-pydev-undefined-variable-from-import-errors (Eclipse)
# Window -> Preferences -> PyDev -> Editor -> Code Analysis -> Undefined -> Undefined Variable From Import -> Ignore
from rdflib_django.models import Store, NamedGraph, NamespaceModel, URIStatement, LiteralStatement

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from django.views import View
from django.contrib.auth.decorators import login_required
from django.conf import settings

from rdflib_django.utils import get_named_graph

from .classes import Country
from .forms import NamedGraphForm, NamespaceModelForm, URIStatementForm, LiteralStatementForm
from .utils import make_uriref, id_from_uriref, friend_uri, friend_graph

def eu_countries(language=settings.LANGUAGE_CODE):
    return [Country(id=qcode) for qcode in settings.EU_COUNTRY_LABELS.keys()]

def homepage(request):
    return render(request, 'homepage.html')

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

def list_statements(request):
    lang = get_language()
    graph_identifier = make_uriref('http://www.wikidata.org')
    graph = get_named_graph(graph_identifier)
    statement_dicts = [{'graph': 'wikidata', 'subject': friend_uri(s, lang=lang), 'predicate': friend_uri(p, lang=lang), 'object': friend_uri(o, lang=lang)}
                           for s, p, o in graph]
    return render(request, 'list_statements.html', {'statement_dicts': statement_dicts})
        
def view_named_graph(request, named_graph_id):
    named_graph = get_object_or_404(NamedGraph, pk=named_graph_id)
    return render(request, 'named_graph.html', {'named_graph': named_graph})

@method_decorator(login_required, name='post')
class editNamedGraph(View):
    form_class = NamedGraphForm
    template_name = 'edit_named_graph.html'

    def get(self, request, named_graph_id=None):
        if named_graph_id:
            named_graph = get_object_or_404(NamedGraph, pk=named_graph_id) 
            form = self.form_class(instance=named_graph)
        else:
            initial = {}
            form = self.form_class(initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            named_graph = form.save()
            return HttpResponseRedirect('/named_graph/{}/'.format(named_graph.id))
        return render(request, self.template_name, {'form': form})

def view_namespace_model(request, namespace_model_id):
    namespace_model = get_object_or_404(NamespaceModel, pk=namespace_model_id)
    return render(request, 'namespace_model.html', {'namespace_model': namespace_model})

@method_decorator(login_required, name='post')
class editNamespaceModel(View):
    form_class = NamespaceModelForm
    template_name = 'edit_namespace.html'

    def get(self, request, namespace_id=None):
        if namespace_id:
            namespace = get_object_or_404(URIStatement, pk=namespace_id) 
            form = self.form_class(instance=namespace)
        else:
            initial = {}
            form = self.form_class(initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            namespace = form.save()
            return HttpResponseRedirect('/namespace/{}/'.format(namespace.id))
        return render(request, self.template_name, {'form': form})

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

def compare_countries(request):
    countries= []
    post=request.POST
    if post:
        countries_code = post.getlist('group',[])
        for country_code in countries_code:
            assert country_code[0]=='Q'
            country = Country(id=country_code)
            countries.append(country)
    return render(request, 'country.html', {'countries_selected' : countries})
