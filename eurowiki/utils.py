import urllib.request
import json
import hashlib
from rdflib.term import URIRef
from django.conf import settings

wikidata_get_claims_template = 'https://www.wikidata.org/w/api.php?action=wbgetclaims&format=json&rank=normal&property={}&entity={}'
wikidata_image_src_template = 'https://upload.wikimedia.org/wikipedia/commons/{}/{}/{}'

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
    