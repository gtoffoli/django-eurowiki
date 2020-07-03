# see https://stackoverflow.com/questions/2112715/how-do-i-fix-pydev-undefined-variable-from-import-errors (Eclipse)
# Window -> Preferences -> PyDev -> Editor -> Code Analysis -> Undefined -> Undefined Variable From Import -> Ignore
from rdflib.namespace import XSD
from rdflib.term import Literal, BNode

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django import forms
from django.utils.translation import get_language
from django.views import View
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User

from rdflib_django.models import Store, NamedGraph, NamespaceModel, URIStatement, LiteralStatement
from rdflib_django.utils import get_named_graph, get_conjunctive_graph

from .classes import Country, Item, Predicate
from .forms import StatementForm
from .forms import LITERAL_PREDICATE_CHOICES, ITEM_PREDICATE_CHOICES, COUNTRY_PREDICATE_CHOICES
from .utils import datatype_from_id, is_bnode_id, make_node, make_uriref, id_from_uriref, friend_uri, friend_graph


try:
    from commons.models import Project
    euro_project = Project.objects.get(pk=settings.EURO_PROJECT_ID)
except:
    euro_project = None
    
def user_is_member(self, project=euro_project):
    return self.is_authenticated and ((project and project.is_member(self)) or (not project and self.is_full_member()))
User.is_euro_member = user_is_member


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

def view_literal_statement(request, statement_id):
    statement = get_object_or_404(LiteralStatement, pk=statement_id)
    return render(request, 'literal_statement.html', {'statement': statement})

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
    if is_bnode_id(item_code):
        bnode = BNode(item_code)
        item = Item(bnode=bnode)
    else:
        item = Item(id=item_code)
    return render(request, 'item.html', {'item' : item})

def edit_item(request, item_code):
    country=request.GET.get('c')
    predicate=request.GET.get('p')
    predicate1=request.GET.get('p1')
    if len(item_code)==35:
        bnode = BNode(item_code)
        item = Item(bnode=bnode)
    else:
        item = Item(id=item_code)
    return render(request, 'item_edit.html', {'item' : item, 'country' : country, 'predicate' : predicate, 'predicate1' : predicate1})

@method_decorator(login_required, name='post')
class editItem(View):
    template_name = 'edit_item.html'

    def get(self, request, item_code):
        c = request.GET.get('c')
        country = Country(id=c)
        p = request.GET.get('p')
        predicate = Predicate(id=p)
        p1 = request.GET.get('p1')
        predicate1 = p1 and Predicate(id=p1) or None
        if is_bnode_id(item_code):
            bnode = BNode(item_code)
            item = Item(bnode=bnode)
        else:
            item = Item(id=item_code)
        return render(request, self.template_name, {'item': item, 'country': country, 'predicate': predicate, 'predicate1': predicate1})

    def post(self, request):
        save = request.POST.get('save', False)
        save_continue = request.POST.get('continue', False)
        item_code = request.POST['item']
        if is_bnode_id(item_code):
            bnode = BNode(item_code)
            item = Item(bnode=bnode)
            subject = item.bnode
        else:
            item = Item(id=item_code)
            subject = item.uriref
        country_id = request.POST['country']
        country = Country(id=country_id)
        predicate0_id = request.POST['predicate']
        predicate0 = Predicate(id=predicate0_id)
        predicate1_id = request.POST.get('predicate1', '')
        predicate1 = predicate1_id and Predicate(id=predicate1_id) or None
        query_string = '?c={}&p={}&p1={}'.format(country_id, predicate0_id, predicate1_id)
        if save or save_continue:
            conjunctive_graph = get_conjunctive_graph()
        field_dict = {}
        for name, value in request.POST.items():
            if name.count('_'):
                field_dict[name] = value
        for name in field_dict.keys():
            if save or save_continue:
                predicate_id, datatype_id, language = name.split('_')
                predicate = Predicate(id=predicate_id).uriref
                new_value = field_dict[name]
                quads = list(conjunctive_graph.quads((subject, predicate, None)))
                for quad in quads:
                    (subject, predicate, object, graph) = quad
                    old_value = object.value
                    if datatype_id and datatype_id == object.datatype_id():
                        if new_value != old_value:
                            graph.add((subject, predicate, Literal(new_value, datatype=object.datatype)))
                            conjunctive_graph.remove(quad)
                    elif language and language == object.language:
                        if new_value != old_value:
                            graph.add((subject, predicate, Literal(new_value, lang=object.language)))
                            conjunctive_graph.remove(quad)
                    elif not language and not object.language:
                        if new_value != old_value:
                            graph.add((subject, predicate, Literal(new_value)))
                            conjunctive_graph.remove(quad)
        if save:
            return HttpResponseRedirect('/item/{}/{}'.format(item_code, query_string))
        elif save_continue:
            return HttpResponseRedirect('/item/{}/edit/{}'.format(item_code, query_string))
 
@method_decorator(login_required, name='post')
class editStatement(View):
    form_class = StatementForm
    template_name = 'edit_statement.html'

    def get(self, request, statement_id=None, subject_id=None):
        language = get_language()[:2]
        if statement_id:
            statement_class = 'literal' # estrarre dallo statement
            if statement_class=='uri':
                statement = get_object_or_404(URIStatement, pk=statement_id)
            else:
                statement = get_object_or_404(LiteralStatement, pk=statement_id)
            form = self.form_class(instance=statement)
        if subject_id:
            statement_class = 'literal'
            initial = { 'statement_class': 'literal', 'subject': subject_id, 'datatype': 'string', 'language': language }
            form = self.form_class(initial=initial)
            form.fields['object'].widget = forms.HiddenInput()
            # form.fields['datatype'].widget = forms.HiddenInput()
        if statement_class == 'literal':
            form.fields['predicate'].choices = LITERAL_PREDICATE_CHOICES
        else: # uri
            if subject_id in settings.EU_COUNTRY_KEYS:
                form.fields['predicate'].choices = COUNTRY_PREDICATE_CHOICES
            else:
                form.fields['predicate'].choices = ITEM_PREDICATE_CHOICES
        return render(request, self.template_name, {'form':form, 'subject':subject_id, 'statement':statement_id})

    def post(self, request, statement_id=None, subject_id=None):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            predicate = data['predicate']
            context = data['context']
            statement_class = data['statement_class']
            if statement_class == 'literal':
                form.fields['object'].widget = forms.HiddenInput()
                value = data['literal']
                dt = data['datatype']
                language = language = data['language']
                if dt == 'string':
                    datatype = XSD.string
                    if predicate in settings.RDF_I18N_PROPERTIES:
                        o = Literal(value, lang=language)
                    else:
                        o = Literal(value)
                else:
                    form.fields['language'].widget = forms.HiddenInput()
                    form.fields['predicate'].choices = LITERAL_PREDICATE_CHOICES
                    if dt == 'integer':
                        datatype = XSD.integer
                    elif dt == 'date':
                        datatype = XSD.date
                    elif dt == 'gYear':
                        datatype = XSD.integer
                    elif dt == 'gMonthDay':
                        datatype = XSD.string
                    o = Literal(value, datatype=datatype)
                if request.POST.get('save', ''):
                    assert value
                    if dt == 'string':
                        assert language
                    s = make_node(subject_id)
                    p = make_uriref(predicate)
                    c = NamedGraph.objects.get(identifier=make_uriref(context))
                    value = object
                    statement = LiteralStatement(subject=s, predicate=p, object=o, context=c)
                    statement.save()
                    if subject_id in settings.EU_COUNTRY_KEYS:
                        return HttpResponseRedirect('/country/{}/'.format(subject_id))
                    else:
                        return HttpResponseRedirect('/item/{}/edit'.format(subject_id))
            else:  # statement_class=='uri'
                form.fields['literal'].widget = forms.HiddenInput()
                form.fields['datatype'].widget = forms.HiddenInput()
                form.fields['language'].widget = forms.HiddenInput()
                if subject_id in settings.EU_COUNTRY_KEYS:
                    form.fields['predicate'].choices = COUNTRY_PREDICATE_CHOICES
                else:
                    form.fields['predicate'].choices = ITEM_PREDICATE_CHOICES
                if request.POST.get('save', ''):
                    object_id = data['object']
                    assert object_id
                    s = make_node(subject_id)
                    p = make_uriref(predicate)
                    o = make_node(object_id)
                    c = NamedGraph.objects.get(identifier=make_uriref(context))
                    statement = URIStatement(subject=s, predicate=p, object=o, context=c)
                    statement.save()
                    if subject_id in settings.EU_COUNTRY_KEYS:
                        return HttpResponseRedirect('/country/{}/'.format(subject_id))
                    else:
                        return HttpResponseRedirect('/item/{}/'.format(subject_id))
            # statement = form.save()
            # return HttpResponseRedirect('/uri_statement/{}/'.format(statement.id))
        return render(request, self.template_name, {'form': form, 'subject':subject_id, 'statement':statement_id})
