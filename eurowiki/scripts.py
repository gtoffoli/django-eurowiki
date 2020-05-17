import os
import time
import json
import pprint
from urllib.parse import urljoin
import urllib.request
from rdflib.term import BNode, URIRef, Literal
from wikidata.client import Client
from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings
from django.template.defaultfilters import slugify
from rdflib_django.store import DEFAULT_STORE
from rdflib_django.utils import get_named_graph
from rdflib_django.models import Store, NamedGraph, URIStatement, LiteralStatement

wd = 'http://www.wikidata.org/entity/'
wikidata_sparql_endpoint = 'https://query.wikidata.org/sparql'
wikidata_special_entity_json_template = 'https://www.wikidata.org/wiki/Special:EntityData/{}.json'

SLEEP_TIME = 10 # seconds

INSTANCE_OF = 'P31'
SOVEREIGN_STATE = 'Q3624078'
EU = 'Q458'
OF_COUNTRY = 'P17'
MEMBER_OF = 'P463'
NATIONAL_ANTHEM = 'Q23691'
HAS_NATIONAL_ANTHEM = 'P85'
OF = 'P642'
NATIONAL_FLAG = 'Q186516'
HAS_NATIONAL_FLAG = 'P163'
MONUMENT = 'Q4989906'
NATIONAL_SYMBOL = 'Q1128637'
NATIONAL_DAY = 'Q57598'
NATIONAL_MOTTO = 'Q29654714'
HAS_NATIONAL_MOTTO = 'P1546'
NATIONAL_EMBLEM = 'Q1079693'
HAS_NATIONAL_EMBLEM = 'P237'
MUSIC_BY = 'P86'
TEXT_BY = 'P676'

Italy = "Q38"
country_id = Italy

# testing the REST API through the wikidata Client class
def api_explore_country(country_id=country_id):
    client = Client()
    entity = client.get(country_id, load=True)
    print('entity:', entity)
    print('entity type:', entity.type)
    print('id:', entity.id)
    attributes = entity.attributes
    attribute_keys = attributes.keys()
    print(len(attribute_keys), 'attributes')
    print('attribute keys:', attribute_keys)
    print('title:', attributes['title'])
    print('id:', attributes['id'])
    labels = attributes['labels']
    print(len(labels), 'labels')
    print('Italian label:', labels['it'])
    descriptions = attributes['descriptions']
    print(len(descriptions), 'descriptions')
    print('Italian description:', descriptions['it'])
    claims = attributes['claims']
    claim_keys = claims.keys()
    print(len(claim_keys), 'claim keys')
    print('claim keys:', claim_keys)
    memberships = claims[MEMBER_OF]
    print(len(memberships), 'membership claims')
    # print('memberships:', memberships)
    group_ids = [ship['mainsnak']['datavalue']['value']['id'] for ship in memberships] 
    print('belongs to groups:', group_ids)
    groups = []
    for group_id in group_ids[:3]:
        time.sleep(SLEEP_TIME)
        group_entity = client.get(group_id, load=False)
        groups.append(group_entity.attributes['title'])
    print('group titles:', groups)

# get the full set of properties that would be obtained from a wikidata page, without using SPARQL
def wd_get_item_json(wd_item_code):
    url = wikidata_special_entity_json_template.format(wd_item_code)
    with urllib.request.urlopen(url) as opened_url:
        python_data = json.loads(opened_url.read().decode())
    return python_data

# get directly from wikidata API a wide set of properties for all EU countries
# and save each set as a JSON structure in a file identified by country name and code
def wd_dump_eu_countries(path):
    country_codes = settings.EU_COUNTRY_LABELS.keys()
    for wd_item_code in country_codes:
        labels = settings.EU_COUNTRY_LABELS.get(wd_item_code, {})
        if not labels:
            continue
        label = slugify(labels['en'])
        filename = '{}/{}-{}.json'.format(path, label, wd_item_code)
        print(filename)
        time.sleep(SLEEP_TIME)
        python_data = wd_get_item_json(wd_item_code)
        file = open(filename, 'w')
        file.write(json.dumps(python_data))
        file.close()

# get the entities belonging to the EU, and selected related entities, with a sparql query
# from the User Manual: WDQS understands many shortcut abbreviations, known as prefixes. Some are internal to Wikidata,
# e.g. wd, wdt, p, ps, bd, and many others are commonly used external prefixes, like rdf, skos, owl, schema.
# see also: https://towardsdatascience.com/where-do-mayors-come-from-querying-wikidata-with-python-and-sparql-91f3c0af22e2
# TODO: remove UK; remove Netherlands or Kingdom of Netherlands
def sparql_eu_countries(path=None, indent=None):
    sparql = SPARQLWrapper(wikidata_sparql_endpoint)
    sparql.setQuery("""
SELECT ?country ?countryLabel
    ?anthem ?anthemLabel ?anthemDescription
    ?anthem_text_author ?anthem_text_authorLabel
    ?anthem_music_author ?anthem_music_authorLabel
    ?flag ?flagLabel ?flagDescription
    ?emblem ?emblemLabel ?emblemDescription
    ?motto ?mottoLabel ?mottoDescription
WHERE
{{
    ?country wdt:{} wd:{} .
    ?country wdt:{} ?anthem .
    OPTIONAL {{ ?anthem wdt:{} ?anthem_text_author . }}
    OPTIONAL {{ ?anthem wdt:{} ?anthem_music_author . }}
    ?country wdt:{} ?flag .
    ?country wdt:{} ?emblem .
    OPTIONAL {{ ?country wdt:{} ?motto . }}
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "it,en". }}
}}
ORDER BY ASC(?countryLabel)
    """.format(MEMBER_OF, EU, HAS_NATIONAL_ANTHEM, TEXT_BY, MUSIC_BY, HAS_NATIONAL_FLAG, HAS_NATIONAL_EMBLEM, HAS_NATIONAL_MOTTO ))
    sparql.setReturnFormat(JSON)
    eucc = sparql.query().convert() # this is a dict
    if path:
        filepath = os.path.join(path, 'sparql_eu_countries.json')
        f = open(filepath, 'w')
        f.write(json.dumps(eucc))
        f.close
        if indent:
            filepath = os.path.join(path, 'sparql_eu_countries.txt')
            f = open(filepath, 'w')
            f.write(json.dumps(eucc, indent=indent))
            f.close
    else:
        return eucc

# return a list of the wikidata entity codes for the country being members of the EU
def sparql_eu_country_codes():
    sparql = SPARQLWrapper(wikidata_sparql_endpoint)
    sparql.setQuery("""
SELECT ?country WHERE
{{
    ?country wdt:{} wd:{} .
}}
    """.format(MEMBER_OF, EU))
    sparql.setReturnFormat(JSON)
    json = sparql.query().convert()
    country_list = json['results']['bindings']
    country_codes = [c_dict['country']['value'].split('/')[-1] for c_dict in country_list]
    return country_codes

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

# The URI RDFS_LABEL (http://www.w3.org/2000/01/rdf-schema#label) is defined explicitly here, since
# calling URIRef with the base argument (see make_uriref above) seems broken for namespaces ending with "#"
RDFS_LABEL = settings.RDF_PREFIXES['rdfs']+'label'

# def clone_wd_countries_from_query(query_result):
#   c_dict_list = query_result['results']['bindings']
def clone_wd_countries_from_query(data_dict={}, filepath=''):
    if filepath and not data_dict:
        f = open(filepath, 'r')
        data_dict = json.load(f)
    if not data_dict:
        return 'no argument was found'
    c_dict_list = data_dict['results']['bindings']
    store = Store.objects.get(identifier=DEFAULT_STORE)
    graph_identifier = make_uriref('http://www.wikidata.org')
    wikidata_graph, created = NamedGraph.objects.get_or_create(identifier=graph_identifier, store=store)
    if created:
        print('new named graph created:', str(wikidata_graph))
    else:
        print(str(wikidata_graph), 'found')
    context = wikidata_graph
    for c_dict in c_dict_list:
        country = c_dict['country']['value']
        subject = make_uriref(country)
        URIStatement.objects.get_or_create(subject=subject, predicate=make_uriref(INSTANCE_OF), object=make_uriref(SOVEREIGN_STATE), context=context)
        URIStatement.objects.get_or_create(subject=subject, predicate=make_uriref(MEMBER_OF), object=make_uriref(EU), context=context)
        if c_dict.get('anthem', {}):
            anthem = c_dict['anthem']['value']
            anthem_uri = URIRef(anthem)
            URIStatement.objects.get_or_create(subject=subject, predicate=make_uriref(HAS_NATIONAL_ANTHEM), object=anthem_uri, context=context)
        anthemLabel_dict = c_dict['anthemLabel']
        if anthemLabel_dict and anthemLabel_dict['xml:lang']=='en':
            anthemLabel = anthemLabel_dict['value']
            LiteralStatement.objects.get_or_create(subject=anthem_uri, predicate=make_uriref(RDFS_LABEL), object=Literal(anthemLabel), context=context)
        if c_dict.get('anthem_text_author', {}):
            anthem_text_author = c_dict['anthem_text_author']['value']
            anthem_text_author_uri = URIRef(anthem_text_author)
            URIStatement.objects.get_or_create(subject=anthem_uri, predicate=make_uriref(TEXT_BY), object=anthem_text_author_uri, context=context)
        anthem_text_authorLabel_dict = c_dict.get('anthem_text_authorLabel', {})
        if anthem_text_authorLabel_dict and anthem_text_authorLabel_dict['xml:lang']=='en':
            anthem_text_authorLabel = anthem_text_authorLabel_dict['value']
            LiteralStatement.objects.get_or_create(subject=anthem_text_author_uri, predicate=make_uriref(RDFS_LABEL), object=Literal(anthem_text_authorLabel), context=context)
        if c_dict.get('anthem_music_author', {}):
            anthem_music_author = c_dict['anthem_music_author']['value']
            anthem_music_author_uri = URIRef(anthem_music_author)
            URIStatement.objects.get_or_create(subject=anthem_uri, predicate=make_uriref(MUSIC_BY), object=anthem_music_author_uri, context=context)
        anthem_music_authorLabel_dict = c_dict.get('anthem_music_authorLabel', {})
        if anthem_music_authorLabel_dict and anthem_music_authorLabel_dict.get('xml:lang', '')=='en':
            anthem_music_authorLabel = anthem_music_authorLabel_dict['value']
            LiteralStatement.objects.get_or_create(subject=anthem_music_author_uri, predicate=make_uriref(RDFS_LABEL), object=Literal(anthem_music_authorLabel), context=context)
        if c_dict.get('flag', {}):
            flag = c_dict['flag']['value']
            flag_uri = URIRef(flag)
            URIStatement.objects.get_or_create(subject=subject, predicate=make_uriref(HAS_NATIONAL_FLAG), object=flag_uri, context=context)
        flagLabel_dict = c_dict.get('flagLabel', {})
        if flagLabel_dict and flagLabel_dict.get('xml:lang', '')=='en':
            flagLabel = flagLabel_dict['value']
            LiteralStatement.objects.get_or_create(subject=flag_uri, predicate=make_uriref(RDFS_LABEL), object=Literal(flagLabel), context=context)
        if c_dict.get('emblem', {}):
            emblem = c_dict['emblem']['value']
            emblem_uri = URIRef(emblem)
            URIStatement.objects.get_or_create(subject=subject, predicate=make_uriref(HAS_NATIONAL_EMBLEM), object=emblem_uri, context=context)
        emblemLabel_dict = c_dict.get('emblemLabel', {})
        if emblemLabel_dict and emblemLabel_dict.get('xml:lang', '')=='en':
            emblemLabel = emblemLabel_dict['value']
            LiteralStatement.objects.get_or_create(subject=subject, predicate=make_uriref(RDFS_LABEL), object=Literal(emblemLabel), context=context)
            
def clone_wd_countries_from_json(filepath):
    pass

# create or update from a dict the statements describing a wd item
# inside the tree, derived form JSON, describing an EU country
def load_item_from_dict(item_dict, wd_item_code, langs):
    item_property_keys = item_dict.keys()
    print('keys:', item_property_keys)
    assert item_dict['type']=='item'
    assert item_dict['id']==wd_item_code
    labels = item_dict['labels']
    print(len(labels), 'labels')
    for lang in langs:
        label = labels.get(lang, '')
        if label:
            print (lang, 'label:', label['value'])
    descriptions = item_dict['descriptions']
    print(len(descriptions), 'descriptions')
    for lang in langs:
        description = descriptions.get(lang, '')
        if description:
            print (lang, 'description:', description['value'])
    claims =  item_dict['claims']
    print(len(claims), 'claims')
    for key in settings.PREDICATE_LABELS.keys():
        statements = claims.get(key, [])
        if not statements:
            continue
        print('claim:', key, len(statements), 'statements')
        for s in statements[:1]:
            mainsnak = s.get('mainsnak', {})
            if not mainsnak:
                continue
            datatype = mainsnak['datatype']
            # print('datatype:', datatype)
            if datatype=='wikibase-item':
                property = mainsnak['property']
                label = settings.PREDICATE_LABELS.get(key, {}).get('en', '')
                value = mainsnak['datavalue']['value']['id']
                print('{} ({}): {}'.format(property, label, value))

# create or update the statements describing an EU country from JSON data
# that were dumped starting from a wikidata item
def load_item_from_file(filepath, langs=['en', 'it',]):
    print('load_item_from_file', filepath)
    file = open(filepath, 'r')
    data = json.loads(file.read())
    file.close()
    value = data['entities']
    wd_item_code = list(value.keys())[0]
    item_dict = value[wd_item_code]
    load_item_from_dict(item_dict, wd_item_code, langs)

# export to RDF or N3 file the entire "wikidata" graph from the eurowiki DB
def export_countries(format="rdf"):
    store = Store.objects.get(identifier=DEFAULT_STORE)
    graph_identifier = make_uriref('http://www.wikidata.org')
    wikidata_graph = NamedGraph.objects.get(identifier=graph_identifier, store=store)
    target = "/tmp/countries.{}".format(format)
    graph = get_named_graph(make_uriref('http://www.wikidata.org'))
    graph.serialize(target, format=format)
 
"""
SELECT
    ?country ?countryLabel
    ?anthem ?anthemLabel ?anthemDescription
    ?anthem_text_author ?anthem_text_authorLabel ?anthem_text_authorDescription
    ?anthem_music_author ?anthem_music_authorLabel ?anthem_music_authorDescription
    ?flag ?flagLabel ?flagDescription
    ?emblem ?emblemLabel ?emblemDescription
    ?motto ?mottoLabel ?mottoDescription
WHERE
{
    ?country wdt:P463 wd:Q458 .
    ?country wdt:P85 ?anthem .
    OPTIONAL { ?anthem wdt:P676 ?anthem_text_author . }
    OPTIONAL { ?anthem wdt:P86 ?anthem_music_author . }
    ?country wdt:P163 ?flag .
    ?country wdt:P237 ?emblem .
    OPTIONAL { ?country wdt:P1546 ?motto . }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
}
ORDER BY ASC(?countryLabel)
"""