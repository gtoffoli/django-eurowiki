# see https://stackoverflow.com/questions/2112715/how-do-i-fix-pydev-undefined-variable-from-import-errors (Eclipse)
# Window -> Preferences -> PyDev -> Editor -> Code Analysis -> Undefined -> Undefined Variable From Import -> Ignore

import json
from datetime import datetime

from rdflib.namespace import XSD
from rdflib.term import Literal, BNode, URIRef

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django import forms
from django.utils.translation import get_language, gettext_lazy as _
from django.views import View
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.flatpages.models import FlatPage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from dal import autocomplete

from rdflib_django.models import Store, NamedGraph, NamespaceModel, URIStatement, LiteralStatement
from rdflib_django.utils import get_named_graph, get_conjunctive_graph

from .models import StatementExtension, SparqlQuery
from .classes import Country, Item, Predicate, StatementProxy
from .forms import StatementForm, QueryForm, QueryExecForm, apply_language_priorities
from .forms import LITERAL_PREDICATE_CHOICES, ITEM_PREDICATE_CHOICES, COUNTRY_PREDICATE_CHOICES, LANGUAGE_CHOICES
from .sparql import run_query, query_result_to_dataframe, dataframe_to_html, dataframe_to_csv
from .sparql import get_query_variables, get_language_parameters
from .utils import is_bnode_id, node_id, make_node, remove_node, make_uriref, id_from_uriref, friend_uri, friend_graph

def eu_countries(language=settings.LANGUAGE_CODE):
    return [Country(id=qcode) for qcode in settings.EU_COUNTRY_LABELS.keys()]

def item_from_id(item_code):
    if is_bnode_id(item_code):
        return Item(bnode=BNode(item_code))
    else:
        return Item(id=item_code)

def robots(request):
    response = render(request, 'robots.txt')
    response['Content-Type'] = 'text/plain; charset=utf-8'
    return response

def homepage(request):
    try:
        page_content = FlatPage.objects.get(url='/eurowiki_home/').content
    except:
        page_content = _('No homepage is present yet.')
    return render(request, 'homepage.html', {'page_content': page_content})

def search(request):
    return render(request, 'search.html')

def comparison(request):
    try:
        page_content = FlatPage.objects.get(url='/eurowiki_comparison/').content
    except:
        page_content = _("The page you are looking for is not yet present.")
    return render(request, 'help.html', {'page_content': page_content})

# forum: https://www.commonspaces.eu/forum/c/project-forums/university-4-europe-european-national-identities-profiles-towards-euroforge/
def contributions(request):
    try:
        page_content = FlatPage.objects.get(url='/eurowiki_contributions/').content
    except:
        page_content = _("The page you are looking for is not yet present.")
    return render(request, 'help.html', {'page_content': page_content})

def help(request):
    try:
        page_content = FlatPage.objects.get(url='/eurowiki_help/').content
    except:
        page_content = _("The page you are looking for is not yet present.")
    return render(request, 'help.html', {'page_content': page_content})

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
    lang = get_language()[:2]
    statements = URIStatement.objects.all().order_by('context', 'subject', 'predicate')
    statements = sorted(statements, key=lambda s: settings.ORDERED_PREDICATE_KEYS.index(id_from_uriref(s.predicate)))
    statement_dicts = [{'graph': friend_graph(s.context), 'subject': friend_uri(s.subject, lang=lang), 'predicate': friend_uri(s.predicate, lang=lang), 'object': friend_uri(s.object, lang=lang)}
                       for s in statements]
    return render(request, 'list_uri_statements.html', {'statement_dicts': statement_dicts})

def list_literal_statements(request):
    lang = get_language()[:2]
    statements = LiteralStatement.objects.all().order_by('context', 'subject', 'predicate')
    statement_dicts = [{'graph': friend_graph(s.context), 'subject': friend_uri(s.subject, lang=lang), 'predicate': friend_uri(s.predicate, lang=lang), 'object': str(s.object)}
                       for s in statements]
    return render(request, 'list_literal_statements.html', {'statement_dicts': statement_dicts})

def list_statements(request, graph_identifier=None):
    lang = get_language()[:2]
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

# statement_extension = None
def statement_comments(request, statement_id):
    statement_proxy = StatementProxy(statement_id=statement_id)
    statement = statement_proxy.statement
    statement_extension = statement_proxy.extension
    if not statement_extension:
        statement_extension = StatementExtension() # can be non-persistent object
        if isinstance(statement, LiteralStatement):
            statement_extension.literal_statement = statement
        else:
            statement_extension.uri_statement = statement
        statement_extension.save()
    data_dict = {'statement_extension': statement_extension, 'can_comment': True}
    """
    subject_id = node_id(statement.subject)
    if subject_id in settings.EU_COUNTRY_KEYS:
        item = Country(id=subject_id)
        data_dict['country'] = item
    else:
        item = Item(id=subject_id)
    """
    subject = statement.subject
    subject_id = node_id(subject)
    if subject_id in settings.EU_COUNTRY_KEYS:
        item = Country(id=subject_id)
        data_dict['country'] = item
    else:
        if isinstance(subject, BNode):
            item = Item(bnode=subject)
        else:
            item = Item(uriref=subject)
    data_dict['item'] = item
    breadcrumb = make_breadcrumb(request, item)
    data_dict['country_list'] = breadcrumb[0]
    data_dict['country_parent_list'] = breadcrumb[1]
    data_dict['predicate'] = breadcrumb[2]
    data_dict['predicate1'] = breadcrumb[3]
    statement_predicate = Predicate(statement.predicate)
    data_dict['statement_predicate'] = statement_predicate
    return render(request, 'statement_comments.html', data_dict)

def view_country(request, item_code):
    assert item_code[0]=='Q'
    countries = []
    country = Country(id=item_code)
    countries.append(country)
    lineages = country.lineages(request)
    return render(request, 'country.html', {'countries_selected' : countries, 'filter_predicate': None})

def view_countries(request):
    countries= []
    filter_predicate = None
    post=request.POST
    if post:
        countries_code = post.getlist('group',[])
        filter_predicate = post.get('filter_prop')
        for country_code in countries_code:
            assert country_code[0]=='Q'
            country = Country(id=country_code)
            countries.append(country)
            lineages = country.lineages(request)
    return render(request, 'country.html', {'countries_selected' : countries, 'filter_predicate': filter_predicate})

def make_breadcrumb(request,item):
    country_list = []
    country_parent_list = {}
    predicate_list = []
    parent_list = []
    predicate = None
    predicate1 = None
    lineages = item.lineages(request)
    for lineage in lineages:
        for e in lineage:
            if e[0].id in settings.EU_COUNTRY_KEYS:
                last_country = Country(id=e[0].id)
                country = [ country for country in country_list if country.id == last_country.id]
                if not country:
                    country_list.append (last_country)
                    parent_list = []
                predicate_list.append (Predicate(id=e[1].id))
                label = str(e[0].id)
            else:
                predicate1 = e[1] and Predicate(id=e[1].id) or None
                if predicate1:
                    l_tmp =[]
                    if predicate_list:
                        l_tmp.append(predicate_list.pop())
                    """
                    if is_bnode_id(e[0].id):
                        l_tmp.append(Item(bnode=BNode(e[0].id)))
                    else:
                        l_tmp.append(Item(id=e[0].id) or None)
                    """
                    l_tmp.append(e[0])
                    parent_list.append(l_tmp)
                    country_parent_list[label] = parent_list
    for key in country_parent_list:
        new_list_values = []
        list_values = country_parent_list[key]
        for e in COUNTRY_PREDICATE_CHOICES:
            e = list(e)
            for v in list_values:
                if v[0].id == e[0]:
                    new_list_values.append(v)
        if new_list_values:
            country_parent_list[key] = new_list_values
    if len(predicate_list) == 1:
        predicate = predicate_list.pop()
    return [country_list, country_parent_list, predicate, predicate1]

def view_item(request, item_code):
    item = item_from_id(item_code)
    breadcrumb = make_breadcrumb(request,item)
    return render(request, 'item.html', {'item' : item, 'country_list' : breadcrumb[0], 'country_parent_list': breadcrumb[1], 'predicate' : breadcrumb[2], 'predicate1' : breadcrumb[3]})

@csrf_exempt
def viewProperty(request, item_code):
    item = item_from_id(item_code)
    property = request.POST.get('p')
    language = request.POST.get('lang', None)
    if property == 'label':
        properties = item.properties(keys=[property], exclude_keys=[], language=language)
    else:
        properties = item.properties(keys=[property], language=language)
    if len(properties) == 1:
        # for p, o, lang, languages, c, r, previous_p in properties:
        for p, o, lang, languages, c, r, s, previous_p in properties:
            if property != 'label':
                o = o.replace('\n', '<br>')
            return JsonResponse({"json_data": o })

@login_required
def remove_item(request, item_code, graph_identifier=None):
    if graph_identifier:
        graph = get_named_graph(graph_identifier)
    else:
        graph = get_conjunctive_graph()
    item = item_from_id(item_code)
    lineages = item.lineages(request)
    parent, predicate = lineages[0][-1]
    parent_code = parent.id
    node = item.uriref
    in_triple = next(graph.triples((parent.uriref, predicate.uriref, node)))
    graph.remove(in_triple)
    remove_node(node, graph)
    if parent_code in settings.EU_COUNTRY_KEYS:
        return HttpResponseRedirect('/country/{}/'.format(parent_code))
    else:
        return HttpResponseRedirect('/item/{}/'.format(parent_code))

@login_required
def removeProperty(request, item_code, graph_identifier=None):
    if graph_identifier:
        graph = get_named_graph(graph_identifier)
    else:
        graph = get_conjunctive_graph()
    subject = make_node(item_code)
    country_id = request.GET.get('c')
    property = make_node(request.GET.get('p'))
    datatype_id = request.GET.get('dt')
    object_value_or_id = request.GET.get('o')
    language = request.GET.get('lang', None)
    triples = graph.triples((subject, property, None))
    for triple in triples:
        object = triple[2]
        if isinstance(object, Literal):
            if datatype_id:
                if datatype_id == object.datatype_id() and object_value_or_id == str(object.value):
                    graph.remove(triple)
            elif language and object.language and (language == object.language) and (object_value_or_id == object.value):
                graph.remove(triple)
            elif language and not object.language and (object_value_or_id == object.value):
                graph.remove(triple)
            elif not language and not object.language and (object_value_or_id == object.value):
                graph.remove(triple)
            elif object_value_or_id == str(object.value):
                graph.remove(triple)
            """ MMR 200723
            elif language and language == object.language:
                graph.remove(triple)
            elif not language and not object.language:
                graph.remove(triple)
            """
        else:
            if isinstance(object, BNode):
                if object_value_or_id == str(object):
                    remove_node(object, graph)
                    graph.remove(triple)
            elif isinstance(object, URIRef):
                if id_from_uriref(object) == object_value_or_id:
                    remove_node(object, graph)
                    graph.remove(triple)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@method_decorator(login_required, name='post')
class editItem(View):
    template_name = 'edit_item.html'

    def get(self, request, item_code):
        item = item_from_id(item_code)
        breadcrumb = make_breadcrumb(request,item)
        return render(request, self.template_name, {'item' : item, 'country_list' : breadcrumb[0], 'country_parent_list': breadcrumb[1], 'predicate' : breadcrumb[2], 'predicate1' : breadcrumb[3]})

    def post(self, request):
        save = request.POST.get('save', False)
        save_continue = request.POST.get('continue', False)
        item_code = request.POST['item']
        if is_bnode_id(item_code):
            item = Item(bnode=BNode(item_code))
            subject = item.bnode
        else:
            item = Item(id=item_code)
            subject = item.uriref
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
            return HttpResponseRedirect('/item/{}/'.format(item_code))
        elif save_continue:
            return HttpResponseRedirect('/item/{}/edit/'.format(item_code))

@method_decorator(login_required, name='post')
class editStatement(View):
    form_class = StatementForm
    template_name = 'edit_statement.html'

    def get(self, request, statement_id=None, subject_id=None):
        data_dict = {}
        fun = request.GET.get('f')
        data_dict['fun'] = fun
        language = get_language()[:2]
        subject = item_from_id(subject_id)
        data_dict['subject'] = subject
        is_country = subject_id in settings.EU_COUNTRY_KEYS
        data_dict['is_country'] = is_country
        if is_country:
            country = Country(id=subject_id)
            data_dict['country'] = country
            statement_class = 'uri'
        else:
            statement_class = 'literal'
        context = settings.DEFAULT_CONTEXT
        initial = { 'statement_class': statement_class, 'subject': subject_id, 'datatype': 'string', 'language': '', 'object_node_type': 'old', 'context': context }
        form = self.form_class(initial=initial)
        form.fields['subject'].widget = forms.HiddenInput()
        breadcrumb = make_breadcrumb(request,subject)
        data_dict['country_list'] = breadcrumb[0]
        data_dict['country_parent_list'] = breadcrumb[1]
        data_dict['predicate'] = predicate0 = breadcrumb[2]
        data_dict['predicate1'] = predicate1 = breadcrumb[3]

        if statement_class == 'literal':
            if predicate1 or predicate0:
                if predicate1 and predicate1.id in settings.EW_SUBTREE_KEYS:
                    list_tmp = settings.EW_SUBTREE[predicate1.id]
                    form.fields['statement_class'].widget = forms.HiddenInput()
                elif predicate0 and predicate0.id in settings.EW_TREE_KEYS:
                    list_tmp = settings.EW_TREE[predicate0.id]
                v = list(LITERAL_PREDICATE_CHOICES[0]) # 'label' is expected to be in 1st position !!!
                v[1] = settings.PREDICATE_LABELS[v[0]][language]
                predicate_list = [ tuple(v)] 
                for p in list_tmp:
                    for v in LITERAL_PREDICATE_CHOICES:
                        if p == v[0]:
                            v = list(v)
                            v[1] = settings.PREDICATE_LABELS[v[0]][language]
                            predicate_list.append(tuple(v))
                form.fields['predicate'].choices = predicate_list
            else:
                form.fields['predicate'].choices = LITERAL_PREDICATE_CHOICES
            form.fields['object'].widget = forms.HiddenInput()
            form.fields['object_node_type'].widget = forms.HiddenInput()
        else: # uri
            form.fields['statement_class'].widget = forms.HiddenInput()
            form.fields['datatype'].widget = forms.HiddenInput()
            form.fields['literal'].widget = forms.HiddenInput()
            form.fields['language'].widget = forms.HiddenInput()
            if is_country:
                key = 'P948' # page banner
                predicate_choices = COUNTRY_PREDICATE_CHOICES + [(key, settings.PREDICATE_LABELS[key].get(language, key))]
            else:
                predicate_choices = ITEM_PREDICATE_CHOICES
            props = subject.properties()
            predicate_list = []
            for v in predicate_choices:
                v = list(v)
                v[1] = settings.PREDICATE_LABELS[v[0]][language]
                predicate_list.append(v)
            # for p, o, lang, languages, c, r, previous_p in props:
            for p, o, lang, languages, c, r, s, previous_p in props:
                if p.id in ['P832', 'PUE6',]: # multiple instances of national holidays and monuments are allowed
                    continue
                predicate_list = [v for v in predicate_list if p.id != v[0]]
            form.fields['predicate'].choices = predicate_list
        data_dict['form'] = form
        data_dict['statement'] = statement_id
        return render(request, self.template_name, data_dict, )
        
    def post(self, request, statement_id=None, subject_id=None):
        language = get_language()[:2]
        form = self.form_class(request.POST)
        data_dict = {}
        fun = request.POST.get('fun', '')
        data_dict['fun'] = fun
        is_country = subject_id in settings.EU_COUNTRY_KEYS
        if is_country:
            country = Country(id=subject_id)
            data_dict['country'] = country
        subject = item_from_id(subject_id)
        data_dict['subject'] = subject
        breadcrumb = make_breadcrumb(request, subject)
        data_dict['country_list'] = breadcrumb[0]
        data_dict['country_parent_list'] = breadcrumb[1]
        data_dict['predicate'] = predicate0 = breadcrumb[2]
        data_dict['predicate1'] = predicate1 = breadcrumb[3]
        form.fields['subject'].widget = forms.HiddenInput()
        is_save = False
        if form.is_valid():
            data = form.cleaned_data
            predicate = data['predicate']
            context = data['context']
            statement_class = data['statement_class']
            if predicate == 'P948': # page banner
                statement_class = 'literal'
            if statement_class == 'literal':
                datatype = data['datatype']
                if datatype == 'integer':
                    form.fields['literal'].widget = forms.TextInput(attrs={'type': 'number',})
                elif datatype == 'gYear':
                    form.fields['literal'].widget = forms.TextInput(attrs={'type': 'number', 'placeholder':"yyyy",})
                elif datatype == 'date':
                    form.fields['literal'].widget = forms.TextInput(attrs={'type': 'text', 'placeholder':"yyyy-mm-dd", })
                elif datatype == 'string':
                    form.fields['literal'].widget = forms.Textarea(attrs={'rows': 2})
                else:
                    form.fields['literal'].widget = forms.TextInput()
                if predicate1 or predicate0:
                    if predicate1 and predicate1.id in settings.EW_SUBTREE_KEYS:
                        list_tmp = settings.EW_SUBTREE[predicate1.id]
                        form.fields['statement_class'].widget = forms.HiddenInput()
                    elif predicate0 and predicate0.id in settings.EW_TREE_KEYS:
                        list_tmp = settings.EW_TREE[predicate0.id]
                    v = list(LITERAL_PREDICATE_CHOICES[0]) # 'label' is expected to be in 1st position !!!
                    v[1] = settings.PREDICATE_LABELS[v[0]][language]
                    predicate_list = [tuple(v)] 
                    for p in list_tmp:
                        for v in LITERAL_PREDICATE_CHOICES:
                            if p == v[0]:
                                v = list(v)
                                v[1] = settings.PREDICATE_LABELS[v[0]][language]
                                predicate_list.append(tuple(v))
                    form.fields['predicate'].choices = predicate_list
                else:
                    form.fields['predicate'].choices = LITERAL_PREDICATE_CHOICES
                form.fields['object'].widget = forms.HiddenInput()
                form.fields['object_node_type'].widget = forms.HiddenInput()
                value = data['literal']
                dt = data['datatype']
                language = data['language']
                if dt in ['string', 'gMonthDay',]:
                    datatype = XSD.string
                    if predicate in settings.RDF_I18N_PROPERTIES:
                        o = Literal(value, lang=language)
                    else:
                        o = Literal(value)
                else:
                    form.fields['language'].widget = forms.HiddenInput()
                    """ MMR 200723
                    if dt == 'integer':
                        datatype = XSD.integer
                    elif dt == 'date':
                        datatype = XSD.date
                    elif dt == 'gYear':
                        datatype = XSD.integer
                    elif dt == 'gMonthDay':
                        datatype = XSD.string
                    """
                    if dt in ['integer', 'gYear']:
                        datatype = XSD.integer
                    elif dt == 'date':
                        datatype = XSD.date 
                    o = Literal(value, datatype=datatype)
                if request.POST.get('save', ''):
                    if value:
                        s = make_node(subject_id)
                        p = make_uriref(predicate)
                        c = NamedGraph.objects.get(identifier=make_uriref(context))
                        value = object
                        statement = LiteralStatement(subject=s, predicate=p, object=o, context=c)
                        statement.save()
                        is_save = True
            else:  # statement_class=='uri'
                form.fields['literal'].widget = forms.HiddenInput()
                form.fields['datatype'].widget = forms.HiddenInput()
                form.fields['language'].widget = forms.HiddenInput()
                if is_country:
                    form.fields['statement_class'].widget = forms.HiddenInput()
                    props = country.properties()
                    predicate_list =[]
                    for v in COUNTRY_PREDICATE_CHOICES:
                        v = list(v)
                        v[1] = settings.PREDICATE_LABELS[v[0]][language]
                        predicate_list.append(v)
                    # for p, o, lang, languages, c, r, previous_p in props:
                    for p, o, lang, languages, c, r, s, previous_p in props:
                        if p.id in ['P832', 'PUE6',]: # multiple instances of national holidays and monuments are allowed
                            continue
                        predicate_list = [v for v in predicate_list if p.id != v[0]]
                    form.fields['predicate'].choices = predicate_list
                else:
                    predicate_list = []
                    if predicate0 and predicate0.id in settings.EW_TREE_KEYS:
                        list_tmp = settings.EW_TREE[predicate0.id]
                        for p in list_tmp:
                            for v in ITEM_PREDICATE_CHOICES:
                                if p == v[0]:
                                    v = list(v)
                                    v[1] = settings.PREDICATE_LABELS[v[0]][language]
                                    predicate_list.append(tuple(v))
                    form.fields['predicate'].choices = predicate_list
                object_node_type = data['object_node_type']
                if object_node_type=='old':
                    form.fields['object'] = forms.ChoiceField(required=False, choices=[], label=_('object'), widget = autocomplete.ListSelect2(url='old-item-autocomplete', attrs={'class':'form-control', 'style': 'width: 100%;'}))
                else:
                    form.fields['object'] = forms.CharField(required=False, label=_('object'), widget=forms.TextInput(attrs={'class':'form-control',}))
                if request.POST.get('save', ''):
                    object_id = data['object']
                    o = None
                    if object_node_type=='new':
                        if object_id:
                            o = BNode(object_id.replace('_:', ''))
                        else:
                            o = BNode()
                    elif object_node_type=='old' and object_id:
                        o = make_node(object_id)
                    elif object_node_type=='ext' and object_id.startswith('Q') and object_id[1:].isdecimal(): # ext
                        o = make_node(object_id)
                    if o:
                        s = make_node(subject_id)
                        p = make_uriref(predicate)
                        c = NamedGraph.objects.get(identifier=make_uriref(context))
                        statement = URIStatement(subject=s, predicate=p, object=o, context=c)
                        statement.save()
                        is_save = True
            if is_save:
                if is_country:
                    return HttpResponseRedirect('/country/{}/'.format(subject_id))
                else:
                    if fun == 'edit':
                        return HttpResponseRedirect('/item/{}/edit/'.format(subject_id))
                    return HttpResponseRedirect('/item/{}/'.format(subject_id))
        data_dict['form'] = form
        data_dict['statement'] = statement_id
        return render(request, self.template_name, data_dict)

class Query(View):
    form_class = QueryForm
    template_name = 'query.html'

    def get(self, request, query_id='', edit_query_id='', run_query_id='', delete_query_id='', query_exec_form = None, languages = None, columns=None, output_mode='show'):
        if languages:
            l1 = languages[0]
            l2 = languages[1]
        else:
            languages = settings.LANGUAGE_CODES[:2]
            l1 = get_language()[:2]
            if languages[0]==l1:
                l2 = languages[1]
            else:
                l2 = languages[0]
                languages[0] = l1
                languages[1] = l2
        data_dict = {}
        if run_query_id:
            query_id = run_query_id
            query = get_object_or_404(SparqlQuery, pk=query_id)
            query_text = query.text.replace('$L1', l1).replace('$L2', l2)
            variables = get_query_variables(query_text)
            columns = columns or variables
            query_result = run_query(query_text)
            dataframe = query_result_to_dataframe(query_result, columns, variables)
            if output_mode=='export':
                query_result = dataframe_to_csv(dataframe)
                response = HttpResponse(query_result)
                mimetype = 'application/vnd.ms-excel'
                response['Content-Type'] = '{}; charset=utf-8'.format(mimetype)
                filename = slugify(query.title)
                timestamp = str(datetime.now())
                response['Content-Disposition'] = 'attachment; filename="{}-{}.csv"'.format(filename, timestamp)
                return response
            query_result = dataframe_to_html(dataframe)
            data_dict['query_result'] = query_result
            data_dict['dataframe'] = not dataframe.empty
        elif query_id:
            query = get_object_or_404(SparqlQuery, pk=query_id)
            query_text = query.text.replace('$L1', l1).replace('$L2', l2)
            variables = get_query_variables(query_text)
        elif edit_query_id:
            query = get_object_or_404(SparqlQuery, pk=edit_query_id)
            data_dict['query'] = query
            form = self.form_class(instance=query)
            data_dict['edit_form'] = form
        elif delete_query_id:
            query = get_object_or_404(SparqlQuery, pk=delete_query_id)
            query.delete()
            return HttpResponseRedirect('/query/')
        else:
            queries = SparqlQuery.objects.all().order_by('title')
            data_dict['queries'] = queries
            query = queries and queries[0] or None
        if query_id or run_query_id:
            data_dict['query'] = query
            data_dict['language_parameters'] = get_language_parameters(query.text)
            if run_query_id:
                if languages:
                    query_exec_form.fields['languages'].choices = apply_language_priorities(LANGUAGE_CHOICES, languages)
                # query_exec_form.fields['columns'].choices = [[c, c] for c in columns]
            else:
                query_exec_form = QueryExecForm()
                query_exec_form.initial = {'query': query_id, 'languages': languages, 'columns': variables, 'output_mode': output_mode}
            query_exec_form.fields['columns'].choices = [[c, c] for c in variables]
            data_dict['query_exec_form'] = query_exec_form
        data_dict['can_edit'] = query and query.can_edit(request)
        data_dict['can_delete'] = query and query.can_delete(request)
        return render(request, self.template_name, data_dict)

    def post(self, request):
        data_dict = {}
        post = request.POST
        if post.get('new_query', ''):
            form = self.form_class()
            data_dict['edit_form'] = form
        elif post.get('save', '') or post.get('save_continue', ''):
            query_id = request.POST.get('id')
            if query_id:
                query = get_object_or_404(SparqlQuery, pk=query_id)
                form = self.form_class(request.POST, instance=query)
            else:
                form = self.form_class(request.POST)
            if form.is_valid():               
                query = form.save(commit=False)
                query.editor = request.user
                query.save()
                if post.get('save', ''):
                    return HttpResponseRedirect('/query/')
            else:
                print (form.errors)
            data_dict['edit_form'] = form
        elif post.get('exec', ''):
            post = request.POST
            query_exec_form = QueryExecForm(post)
            query_id = post.get('query', '')
            query = get_object_or_404(SparqlQuery, pk=query_id)
            columns = get_query_variables(query.text)
            query_exec_form.fields['columns'].choices = [[c, c] for c in columns]
            if query_exec_form.is_valid():
                data = query_exec_form.cleaned_data
                query_id = data['query']
                query = get_object_or_404(SparqlQuery, pk=query_id)
                languages = data['languages']
                columns = data['columns']
                output_mode = data['output_mode']
                return self.get(request, run_query_id=query_id, query_exec_form=query_exec_form, languages=languages, columns=columns, output_mode=output_mode)
            else:
                print (query_exec_form.errors)
        return render(request, self.template_name, data_dict)

def old_item_autocomplete(request):
    MIN_CHARS = 4
    q = request.GET.get('q', None)
    results = []
    if request.user.is_authenticated:
        if q and len(q) >= MIN_CHARS:
            q = q.lower()
            qs = LiteralStatement.objects.filter(predicate__icontains='label', object__icontains=q).order_by('subject')
            last_s = None
            for statement in qs:
                s, p, o = statement.as_triple()
                if s == last_s:
                    continue
                label = o.value
                if label.lower().count(q):
                    last_s = s
                    if isinstance(s, BNode):
                        node_id = str(s)
                    else:
                        node_id = id_from_uriref(s)
                    results.append([node_id, label])
                    last_s = s
            results = sorted(results, key=lambda x: x[1])
            results = [{'id': x[0], 'text': x[1][:80]} for x in results]
    body = json.dumps({ 'results': results, 'more': False, })
    return HttpResponse(body, content_type='application/json')
