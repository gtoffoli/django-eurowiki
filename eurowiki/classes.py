from copy import deepcopy
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import get_language
from rdflib.term import URIRef, BNode, Literal
from rdflib_django.models import URIStatement, LiteralStatement
from rdflib_django.utils import get_named_graph, get_conjunctive_graph
from .utils import is_bnode_id, node_id, make_uriref, id_from_uriref, wd_get_image_url
from .session import get_history
from .models import StatementExtension


RDF_STATEMENT = make_uriref('Statement', prefix='rdf')
RDF_SUBJECT = make_uriref('subject', prefix='rdf')
RDF_PREDICATE = make_uriref('predicate', prefix='rdf')
RDF_OBJECT = make_uriref('object', prefix='rdf')

def get_reified_triples(object, graph):
    reified_triples = []
    reified_statements = list(graph.triples((None, object, RDF_STATEMENT)))
    for statement in reified_statements:
        statement_id = statement[0]
        statement_s = graph.value(subject=statement_id, predicate=RDF_SUBJECT, any=False)
        statement_p = graph.value(subject=statement_id, predicate=RDF_PREDICATE, any=False)
        statement_o = graph.value(subject=statement_id, predicate=RDF_OBJECT, any=False)
        reified_triples.append((statement_s, statement_p, statement_o))
    return reified_triples

class EurowikiBase(object):

    def __init__(self, uriref=None, id=None, bnode=None, graph=None, graph_identifier=None, in_predicate=None):
        assert uriref or id or bnode
        self.uriref = self.id = self.bnode = None
        if uriref:
            self.uriref = uriref
            self.id = id_from_uriref(uriref)
        elif id:
            self.id = id
            self.uriref = make_uriref(id)
        else:
            self.bnode = bnode
            self.id = str(bnode) # added 200708
        if graph_identifier:
            graph = get_named_graph(graph_identifier)
        elif not graph:
            graph = get_conjunctive_graph()
        self.graph = graph
        self.in_predicate = in_predicate

    def labels(self):
        return {}

    def label(self, language=None):
        if not language:
            language = get_language()[:2]
        labels = self.labels()
        lbl = labels.get(language, labels.get('en', ''))
        if not lbl:
            if not self.is_wikidata(): # self.bnode or isinstance(self, BNode): # why these alternatives do not work?
                lbl = settings.UNKNOWN_LABEL_DICT.get(language, '?')
            else:
                lbl = self.id
        return lbl

    def is_bnode(self):
        return self.bnode and not self.uriref

    def is_wikidata(self):
        return self.uriref and self.uriref.count(settings.WIKIDATA_BASE)

    def wd_url(self):
        return self.is_wikidata() and self.uriref.replace('http:', 'https:') or None

class Item(EurowikiBase):

    def url(self):
        if self.is_bnode():
            return '/item/{}/'.format(self.bnode)
        else:
            return '/item/{}/'.format(self.id)

    def node(self):
        return self.uriref or self.bnode

    def node_id(self):
        return node_id(self.node())

    def labels(self):
        return settings.OTHER_ITEM_LABELS.get(self.id, {})
        
    """ MMR 200722
    def preferred_label(self, language=None):
        properties = self.properties(keys=['label',], exclude_keys=[], language=language)
        if properties:
            return properties[0][1]
        if self.is_bnode():
            return self.bnode
        return self.label()
    """

    def preferred_label(self, language=None):
        # properties = self.properties(keys=['label',], exclude_keys=[], language=language)
        properties = self.properties(keys=['label',], exclude_keys=[])
        if properties:
            """ MMR 200725
            if None in properties[0][3]:
                properties[0][3].remove(None)
            if not properties[0][2]:
                properties[0][3] = []
            """
            return [properties[0][1], properties[0][2], properties[0][3]]
        if self.is_bnode():
            return [self.bnode, '', '']
        # return [self.label(), '', '']
        return [super(Item, self).label(), '', '']

    # return a list of paths, each being a list of couples (item, predicate) leading from a country root to the target item
    def lineages(self, request, graph_identifier=None):
        if graph_identifier:
            graph = get_named_graph(graph_identifier)
        else:
            graph = get_conjunctive_graph()
        object = self.node()
        assert object
        MAX_DISTANCE = 5
        MAX_ITERATIONS = 5
        history = get_history(request)
        n_nodes = len(history)
        out_paths = []
        paths = [[[self, None]]] # start with only 1 path containing only a pseudo-edge
        while paths:
            path = paths[0] # 1st path
            object = path[0][0].node() # left element (subject) of first edge becomes target object of previous triples
            triples = list(graph.triples((None, None, object)))
            triples += get_reified_triples(object, graph)
            n_triples = len(triples)
            i = 0
            while n_triples and node_id(object) not in settings.EU_COUNTRY_KEYS:
                i += 1
                if i > MAX_ITERATIONS: # endless loops could result from bugs or wrong network
                    exit
                best_k = 0
                if n_triples > 1:
                    if history:
                        min_distance = MAX_DISTANCE
                        k_range = range(n_triples)
                        for k in k_range:
                            s, p, o = triples[k]
                            if node_id(s) in history:
                                distance = n_nodes - history.index(node_id(s))
                                if distance < min_distance:
                                    best_k = k
                s, p, o = triples[best_k]
                best_edge = [make_item(s), Predicate(uriref=p)]
                del triples[best_k]
                if not history:
                    for triple in triples:
                        edge = [make_item(triple[0]), Predicate(uriref=triple[1])]
                        # paths.append(deepcopy([edge]) + deepcopy(path))
                        paths.append([edge] + path)
                # path = deepcopy([best_edge]) + deepcopy(path)
                path = [best_edge] + path

                object = s
                triples = list(graph.triples((None, None, object)))
                triples += get_reified_triples(object, graph)
                n_triples = len(triples)
            out_paths.append(path[:-1])
            paths = paths[1:]
            # print_paths(out_paths)
        return out_paths

    # def properties(self, keys=[], exclude_keys=['P1476', 'title', 'label',], language=None):
    def properties(self, keys=[], exclude_keys=['label',], language=None, edit=False):

        if not keys:
            in_prop_id = self.in_predicate and self.in_predicate.id or None
            if in_prop_id and in_prop_id in settings.EW_TREE_KEYS:
                keys = settings.EW_TREE[in_prop_id]
            else:
                keys = settings.ORDERED_PREDICATE_KEYS
        # if exclude_keys:
        if exclude_keys and not edit:
            keys = [key for key in keys if not key in exclude_keys]
        if not language:
            language = get_language()[:2]
        # get quads, to include context, remove subject and append placeholder for reified properties
        p_o_c_r_iterable = [[quad[1], quad[2], quad[3], None] for quad in self.graph.quads((self.uriref or self.bnode, None, None))]
        p_o_c_r_iterable = [[p, o, c, r] for p, o, c, r in p_o_c_r_iterable if id_from_uriref(p) in keys]
        # handle reified properties and build a triple for each
        quads = self.graph.quads((None, RDF_SUBJECT, self.uriref or self.bnode))
        for quad in quads:
            reified = quad[0]
            p = self.graph.value(subject=reified, predicate=RDF_PREDICATE)
            if not id_from_uriref(p) in keys:
                continue
            o = self.graph.value(subject=reified, predicate=RDF_OBJECT)
            c = quad[3]
            if reified:
                statements = list(self.graph.quads((reified, None, RDF_STATEMENT, None)))
                if statements:
                    reified = statements[0][1]
                    assert isinstance(reified, BNode)
            p_o_c_r_iterable.append((p, o, c, reified))
        # initialize memory for handling language-aware string literals
        lang_code_dict = {}
        value_dict = {}
        property_dict = {}
        context_dict = {}
        reified_dict = {}
        languages_dict = {}
        statement_dict = {}
        for prop_id in settings.RDF_I18N_PROPERTIES:
            lang_code_dict[prop_id] = None
            value_dict[prop_id] = None
            property_dict[prop_id] = None
            context_dict[prop_id] = None
            reified_dict[prop_id] = None
            languages_dict[prop_id] = []
            statement_dict[prop_id] = None
        props = []
        # iterate on our pseudo-quads
        for p, o, c, r in p_o_c_r_iterable:
            if not keys.count(id_from_uriref(p)):
                continue
            if r:
                o = r # copy URI of reified statement to object
                r = None
            statement_proxy = StatementProxy(subject=self.uriref or self.bnode, predicate=p, object=o)
            p = Predicate(uriref=p, graph=self.graph)
            # if p.is_literal() and not isinstance(o, BNode): # temporary patch
            if p.is_literal():
                if p.is_image():
                    o = Image(o)
                else:
                    prop_id = p.id
                    if prop_id in settings.RDF_I18N_PROPERTIES:
                        lang = o.language
                        if edit:
                            # props.append([p, o.value, lang, [], c, r])
                            props.append([p, o.value, lang, [], c, r, statement_proxy])
                        else:
                            if lang==language:
                                lang_code_dict[prop_id] = lang
                                property_dict[prop_id] = p
                                value_dict[prop_id] = o.value
                                context_dict[prop_id] = c
                                reified_dict[prop_id] = r
                                statement_dict[prop_id] = statement_proxy
                            elif lang==settings.LANGUAGE_CODE:
                                if not value_dict[prop_id]:
                                    lang_code_dict[prop_id] = lang
                                    property_dict[prop_id] = p
                                    value_dict[prop_id] = o.value
                                    context_dict[prop_id] = c
                                    reified_dict[prop_id] = r
                                    statement_dict[prop_id] = statement_proxy
                            elif lang and (not value_dict[prop_id] or (lang_code_dict[prop_id] in settings.LANGUAGE_CODES and lang in settings.LANGUAGE_CODES and settings.LANGUAGE_CODES.index(lang)<settings.LANGUAGE_CODES.index(lang_code_dict[prop_id]))):
                                lang_code_dict[prop_id] = lang
                                property_dict[prop_id] = p
                                value_dict[prop_id] = o.value
                                context_dict[prop_id] = c
                                reified_dict[prop_id] = r
                                statement_dict[prop_id] = statement_proxy
                            elif not property_dict[prop_id]:
                                lang_code_dict[prop_id] = lang
                                property_dict[prop_id] = p
                                value_dict[prop_id] = o.value
                                context_dict[prop_id] = c
                                reified_dict[prop_id] = r
                                statement_dict[prop_id] = statement_proxy
                            # MMR 200725 languages_dict[prop_id].append(lang)
                            if lang:
                                languages_dict[prop_id].append(lang)
                        continue
            else:
                if isinstance(o, BNode):
                    o = Item(bnode=o, graph=self.graph, in_predicate=p)
                else:
                    o = Item(uriref=o, graph=self.graph, in_predicate=p)
                if r:
                    r = Item(bnode=r, graph=self.graph, in_predicate=p)
            # props.append([p, o, '', [], c, r])
            props.append([p, o, '', [], c, r, statement_proxy])
        # append proper version of language-aware string literals
        if not edit:
            for prop_id in settings.RDF_I18N_PROPERTIES:
                if value_dict[prop_id]:
                    # props.append([property_dict[prop_id], value_dict[prop_id], lang_code_dict[prop_id] or '', languages_dict[prop_id], context_dict[prop_id], reified_dict[prop_id]])
                    props.append([property_dict[prop_id], value_dict[prop_id], lang_code_dict[prop_id] or '', languages_dict[prop_id], context_dict[prop_id], reified_dict[prop_id], statement_dict[prop_id]])
        # sort properties at the end of all processing
        props = sorted(props, key=lambda prop: keys.index(prop[0].id))
        # record the previous property and the original DB statement
        # in the tuple itself, so that they can be accessed in template 
        # props_with_pp = []
        props_with_pp_st = []
        previous_p = None
        for prop in props:
            prop.append(previous_p)
            previous_p = prop[0]
            # props_with_pp.append(prop)
            props_with_pp_st.append(prop)
        # return props_with_pp
        return props_with_pp_st

    def edit_properties(self):
        return self.properties(edit=True)

class Country(Item):

    def url(self):
        return '/country/{}/'.format(self.id)

    def labels(self):
        return settings.EU_COUNTRY_LABELS.get(self.id, {})

    # def properties(self):
    def properties(self, keys=[], exclude_keys=['label',], language=None, edit=False):
        return super(Country, self).properties(keys=settings.EU_COUNTRY_PROPERTIES, exclude_keys=exclude_keys, language=language, edit=edit)

    def lineages(self, request, graph_identifier=None):
        return super(Country, self).lineages(request, graph_identifier=graph_identifier)

    def banner_url(self):
        predicate = make_uriref('P948', prefix='wdt')
        banners = list(self.graph.objects(subject=self.uriref, predicate=predicate))
        return banners and wd_get_image_url(banners[0]) or None

class Predicate(EurowikiBase):

    def labels(self):
        return settings.PREDICATE_LABELS.get(self.id, {})

    def is_literal(self):
        return self.id in settings.LITERAL_PROPERTIES

    def is_image(self):
        return self.id in settings.IMAGE_PROPERTIES

    def is_url(self):
        return self.id in settings.URL_PROPERTIES

    def is_repeatable(self):
        return self.id in settings.REPEATABLE_PROPERTIES

class Image(str):

    def __init__(self, name):
        self.name = name

    def url(self):
        return wd_get_image_url(self.name)

def make_item(node):
    if isinstance(node, URIRef):
        if id_from_uriref(node) in settings.EU_COUNTRY_KEYS:
            return Country(uriref=node)
        else:
            return Item(uriref=node)
    elif isinstance(node, BNode):
        return Item(bnode=node)
    else:
        return None

def print_paths(paths):
    print('paths:', [[edge[0].id for edge in path] for path in paths])

class StatementProxy(Predicate):
    """
    like the other classes in this module, StatementProxy encapsulates a rdflib-django3 statement
    to make it available in Django templates
    """

    # should see https://stackoverflow.com/questions/25354834/in-python-return-none-instead-of-creating-new-instance-if-wrong-parameters-ar
    def __init__(self, statement_id=None, subject=None, predicate=None, object=None):
        assert statement_id or (subject and predicate and object)
        if statement_id:
            try:
                statements = LiteralStatement.objects.filter(pk=statement_id)
                statement = statements[0]
            except:
                # statements = get_object_or_404(URIStatement, pk=statement_id)
                statements = URIStatement.objects.filter(pk=statement_id)
                assert statements.count()
                statement = statements[0]
            subject = statement.subject
            object = statement.object
            predicate = statement.predicate
        else:
            try:
                statements = LiteralStatement.objects.filter(subject=subject, predicate=predicate, object=object)
                statement = statements[0]
            except:
                statements = URIStatement.objects.filter(subject=subject, predicate=predicate, object=object)
                assert statements.count()
                statement = statements[0]
        super(StatementProxy, self).__init__(uriref=predicate)
        self.subject = subject
        self.subject = subject
        self.predicate = predicate
        self.statement = statement

    @property
    def extension(self):
        """
        literal statements with same subject and predicate, and different objects
        (maybe objects with different languages or datatypes), share same extension and same comments!
        """
        if isinstance(self.statement, LiteralStatement):
            siblings = LiteralStatement.objects.filter(subject=self.subject, predicate=self.predicate)
            for statement in siblings:
                statement_extensions = StatementExtension.objects.filter(literal_statement=statement)
                if statement_extensions:
                    break
        else:
            statement_extensions = StatementExtension.objects.filter(uri_statement=self.statement)
        return statement_extensions and statement_extensions[0] or None

    def make_extension(self):
        statement_extension = StatementExtension()
        if isinstance(self.statement, LiteralStatement):
            statement_extension.literal_statement = self.statement
        else:
            statement_extension.uri_statement = self.statement
        statement_extension.save()
        return statement_extension

    @property
    def comments(self):
        extension = self.extension
        return extension and extension.comments or []

    @property
    def can_comment(self, request):
        user = request.user
        return user.is_authenticated
