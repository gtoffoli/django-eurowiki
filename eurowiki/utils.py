import urllib.request
import json
import hashlib
from rdflib.term import URIRef, BNode, Literal

from rdflib_django.models import NamedGraph, URIStatement
from django.conf import settings


def literal_datatype_id(self):
    if self.datatype:
        return self.datatype.replace(settings.RDF_PREFIXES['xsd'], '')
    else:
        return ''
Literal.datatype_id = literal_datatype_id

def datatype_from_id(datatype_id):
    return '{}{}'.format(settings.RDF_PREFIXES['xsd'], datatype_id)


wikidata_get_claims_template = 'https://www.wikidata.org/w/api.php?action=wbgetclaims&format=json&rank=normal&property={}&entity={}'
wikidata_image_src_template = 'https://upload.wikimedia.org/wikipedia/commons/{}/{}/{}'

def is_bnode_id(item_code):
    if not item_code:
        return False
    # return item_code.count('_') or len(item_code)==35 or (len(item_code)==9 and item_code[0]!='Q')
    return item_code.count('_') or (len(item_code)>=9 and item_code[0]!='Q')


def make_uriref(value, prefix=None):
    if not prefix:
        if value.startswith('QUE'):
            prefix = 'ew'
        elif value.startswith('Q'):
            prefix = 'wd'
        elif value.startswith('PUE'):
            prefix = 'ewt'
        elif value.startswith('P'):
            prefix = 'wdt'
        elif value in ['label', 'comment', 'seeAlso']:
            prefix = 'rdfs'         
    if prefix:
        base = settings.RDF_PREFIXES[prefix]
        if base.count('-') and base.endswith('#'): # overccome issue in rdflib URIRef
            return URIRef(base + value)
        else:
            return URIRef(value, base=base)
    else:
        return URIRef(value)

def id_from_uriref(uriref):
    label = uriref.split('/')[-1]
    if label.count('#'):
        label = label.split('#')[-1]      
    return label

def make_node(value, prefix=None):
    if is_bnode_id(value):
        return BNode(value.replace('_:', ''))
    else:
        return make_uriref(value, prefix=prefix)

def remove_node(node, graph):
    # do not remove if node is object of other statements
    convergent_triples = graph.triples((None, None, node))
    if len(list(convergent_triples)) > 1:
        return
    # remove out properties and items
    out_triples = graph.triples((node, None, None))
    for out_triple in out_triples:
        o = out_triple[2]
        if isinstance(o, Literal):
            graph.remove(out_triple)
            continue
        else:
            remove_node(o, graph)
            graph.remove(out_triple)

def node_id(node):
    if isinstance(node, BNode):
        # return BNode
        return str(node)
    else:
        return id_from_uriref(node.toPython())

# (re-)generate human-friendly nodeIDs, following a certain pattern; to be tested
def item_uriref_generator(prefix='ew', context=None):
    if not context:
        context = NamedGraph.objects.get_or_create(graph_identifier=make_uriref(settings.EUROWIKI_BASE))
    statements = URIStatement.objects.filter(subject__startswith=settings.RDF_PREFIXES[prefix], context=context).order_by('-subject')
    code_base = settings.URI_LABEL_CODES[prefix]
    if statements:
        value_number = id_from_uriref(statements[0].subject).replace(code_base, '')
        ordinal = int(value_number)
    else:
        ordinal = 0
    ordinal += 1
    value = '{}{:04d}'.format(code_base, ordinal)
    return make_uriref(value, prefix=prefix)

def friend_uri(uriref, append_label=True, lang='en'):
    id = ''
    for short, long in settings.RDF_PREFIX_ITEMS:
        if uriref.startswith(long):
            id = uriref[len(long):]
            uriref = '{}:{}'.format(short, id)
            break
    label = ''
    if append_label and id:
        if id[0] == 'Q':
            labels = settings.EU_COUNTRY_LABELS.get(id, {})
            if not labels:
                labels = settings.OTHER_ITEM_LABELS.get(id, {})
            if labels:
                label = labels[lang]
        # elif id[0] == 'P':
        else:
            labels = settings.PREDICATE_LABELS.get(id, {})
            if labels:
                label = labels[lang]
    if label:
        uriref = '{} ({})'.format(uriref, label)
    return uriref

def friend_graph(context):
    return str(context).split('.')[-2]

def wd_get_item_claims(wd_item_code, wd_prop_code):
    request_url = wikidata_get_claims_template.format(wd_prop_code, wd_item_code)
    with urllib.request.urlopen(request_url) as opened_url:
        python_data = json.loads(opened_url.read().decode())
    return python_data.get('claims', [])

def wd_get_image_url(image_name):
    name = image_name.replace(' ', '_')
    m = hashlib.md5()
    m.update(name.encode('UTF-8'))
    hashed = m.hexdigest()
    a = hashed[:1]
    ab = hashed[:2]
    image_url = wikidata_image_src_template.format(a, ab, name)
    return image_url
    