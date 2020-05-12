# see https://stackoverflow.com/questions/2112715/how-do-i-fix-pydev-undefined-variable-from-import-errors (Eclipse)
# Window -> Preferences -> PyDev -> Editor -> Code Analysis -> Undefined -> Undefined Variable From Import -> Ignore
from rdflib_django.models import Store, NamedGraph, NamespaceModel, URIStatement, LiteralStatement

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from rdflib_django.utils import get_named_graph

from .forms import NamedGraphForm, NamespaceModelForm, URIStatementForm, LiteralStatementForm
from .scripts import make_uri

def uri_to_label(uri):
    label = uri.split('/')[-1]
    return label

from django.conf import settings
def friend_uri(uri, append_label=True, lang='en'):
    code = ''
    for short, long in settings.RDF_PREFIX_ITEMS:
        if uri.startswith(long):
            code = uri[len(long):]
            uri = '{}:{}'.format(short, code)
            break
    label = ''
    if append_label and code:
        if code[0] == 'Q':
            labels = settings.EU_COUNTRY_LABELS.get(code, {})
            if not labels:
                labels = settings.OTHER_ITEM_LABELS.get(code, {})
            if labels:
                label = labels[lang]
        elif code[0] == 'P':
            labels = settings.PREDICATE_LABELS.get(code, {})
            if labels:
                label = labels[lang]
    if label:
        uri = '{} ({})'.format(uri, label)
    return uri

def friend_graph(context):
    return str(context).split('.')[-2]

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
    statements = URIStatement.objects.all().order_by('context', 'subject', 'predicate')
    statements = sorted(statements, key=lambda s: settings.ORDERED_PREDICATE_KEYS.index(uri_to_label(s.predicate)))
    statement_dicts = [{'graph': friend_graph(s.context), 'subject': friend_uri(s.subject), 'predicate': friend_uri(s.predicate), 'object': friend_uri(s.object)}
                       for s in statements]
    return render(request, 'list_uri_statements.html', {'statement_dicts': statement_dicts})

def list_literal_statements(request):
    statements = LiteralStatement.objects.all().order_by('context', 'subject', 'predicate')
    statement_dicts = [{'graph': friend_graph(s.context), 'subject': friend_uri(s.subject), 'predicate': friend_uri(s.predicate), 'object': str(s.object)}
                       for s in statements]
    return render(request, 'list_literal_statements.html', {'statement_dicts': statement_dicts})

def list_statements(request):
    graph_identifier = make_uri('http://www.wikidata.org')
    graph = get_named_graph(graph_identifier)
    statement_dicts = [{'graph': 'wikidata', 'subject': friend_uri(s), 'predicate': friend_uri(p), 'object': friend_uri(o)}
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

def view_item(request, item_id):
    item = None
    return render(request, 'item.html', {'item': item})
