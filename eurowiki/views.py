# see https://stackoverflow.com/questions/2112715/how-do-i-fix-pydev-undefined-variable-from-import-errors (Eclipse)
# Window -> Preferences -> PyDev -> Editor -> Code Analysis -> Undefined -> Undefined Variable From Import -> Ignore
from rdflib_django.models import Store, NamedGraph, NamespaceModel, URIStatement, LiteralStatement

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required

from .forms import NamedGraphForm, NamespaceModelForm, URIStatementForm, LiteralStatementForm

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
    uri_statements = URIStatement.objects.all()
    return render(request, 'list_uri_statements.html', {'uri_statements': uri_statements})

def list_literal_statements(request):
    literal_statements = LiteralStatement.objects.all()
    return render(request, 'list_literal_statements.html', {'literal_statements': literal_statements})

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
