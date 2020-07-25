# see https://stackoverflow.com/questions/2112715/how-do-i-fix-pydev-undefined-variable-from-import-errors (Eclipse)
# Window -> Preferences -> PyDev -> Editor -> Code Analysis -> Undefined -> Undefined Variable From Import -> Ignore

import json

from rdflib.namespace import XSD
from rdflib.term import Literal, BNode, URIRef

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django import forms
from django.utils.translation import get_language, ugettext_lazy as _
from django.views import View
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from dal import autocomplete

from rdflib_django.models import Store, NamedGraph, NamespaceModel, URIStatement, LiteralStatement
from rdflib_django.utils import get_named_graph, get_conjunctive_graph

from .classes import Country, Item, Predicate
from .forms import StatementForm
from .forms import LITERAL_PREDICATE_CHOICES, ITEM_PREDICATE_CHOICES, COUNTRY_PREDICATE_CHOICES
from .utils import is_bnode_id, make_node, remove_node, make_uriref, id_from_uriref, friend_uri, friend_graph

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

def item_from_id(item_code):
    if is_bnode_id(item_code):
        return Item(bnode=BNode(item_code))
    else:
        return Item(id=item_code)

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
        for p, o, lang, languages, c, r, previous_p in properties:
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
                predicate_choices = COUNTRY_PREDICATE_CHOICES
            else:
                predicate_choices = ITEM_PREDICATE_CHOICES
            props = subject.properties()
            predicate_list = []
            for v in predicate_choices:
                v = list(v)
                v[1] = settings.PREDICATE_LABELS[v[0]][language]
                predicate_list.append(v)
            for p, o, lang, languages, c, r, previous_p in props:
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
                    for p, o, lang, languages, c, r, previous_p in props:
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
                        return HttpResponseRedirect('/item/{}/edit'.format(subject_id))
                    return HttpResponseRedirect('/item/{}/'.format(subject_id))
        data_dict['form'] = form
        data_dict['statement'] = statement_id
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
