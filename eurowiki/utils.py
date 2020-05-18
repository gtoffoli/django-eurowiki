from rdflib.term import URIRef
from django.conf import settings

def make_uriref(value, prefix=None):
    if not prefix:
        if value.startswith('Q'):
            prefix = 'wd'
        elif value.startswith('P'):
            prefix = 'wdt'
    if prefix:
        return URIRef(value, base=settings.RDF_PREFIXES[prefix])
    else:
        return URIRef(value)

def id_from_uriref(uriref):
    label = uriref.split('/')[-1]
    if label.count('#'):
        label = label.split('#')[-1]      
    return label

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
