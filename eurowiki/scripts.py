import time
import json
import pprint
from urllib.parse import urljoin
import urllib.request
from rdflib.term import BNode, URIRef, Literal
from wikidata.client import Client
from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings
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
def get_item_json(wd_item_code, write=None):
    url = wikidata_special_entity_json_template.format(wd_item_code)
    with urllib.request.urlopen(url) as opened_url:
        data = json.loads(opened_url.read().decode())
    return data

def old_sparql_eu_countries():
    sparql = SPARQLWrapper(wikidata_sparql_endpoint)
    sparql.setQuery("""
SELECT ?country ?countryLabel
    ?anthem ?anthemLabel ?anthemDescription
    ?anthem_text_author ?anthem_text_authorLabel
    ?anthem_music_author ?anthem_music_authorLabel WHERE
{{
    ?country wdt:{} wd:{} .
    ?country wdt:{} ?anthem .
    OPTIONAL {{ ?anthem wdt:{} ?anthem_text_author . }}
    OPTIONAL {{ ?anthem wdt:{} ?anthem_music_author . }}
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "it". }}
}}
ORDER BY ASC(?countryLabel)
    """.format(MEMBER_OF, EU, HAS_NATIONAL_ANTHEM, TEXT_BY, MUSIC_BY ))
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

# get the entities belonging to the EU, and selected related entities, with a sparql query
# from the User Manual: WDQS understands many shortcut abbreviations, known as prefixes. Some are internal to Wikidata,
# e.g. wd, wdt, p, ps, bd, and many others are commonly used external prefixes, like rdf, skos, owl, schema.
# see also: https://towardsdatascience.com/where-do-mayors-come-from-querying-wikidata-with-python-and-sparql-91f3c0af22e2
# TODO: remove UK; remove Netherlands or Kingdom of Netherlands
def sparql_eu_countries():
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
    return sparql.query().convert()

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

def make_uri(value, prefix=None):
    if not prefix:
        if value.startswith('Q'):
            prefix = 'wd'
        elif value.startswith('P'):
            prefix = 'wdt'
    if prefix:
        return URIRef(value, base=settings.RDF_PREFIXES[prefix])
    else:
        return URIRef(value)

def clone_wd_countries(query_result):
    c_dict_list = query_result['results']['bindings']
    store = Store.objects.get(identifier=DEFAULT_STORE)
    graph_identifier = make_uri('http://www.wikidata.org')
    wikidata_graph, created = NamedGraph.objects.get_or_create(identifier=graph_identifier, store=store)
    for c_dict in c_dict_list:
        country = c_dict['country']['value']
        context = wikidata_graph
        subject = make_uri(country)
        item, created = URIStatement.objects.get_or_create(subject=subject, predicate=make_uri(INSTANCE_OF), object=make_uri(SOVEREIGN_STATE), context=context)
        item, created = URIStatement.objects.get_or_create(subject=subject, predicate=make_uri(MEMBER_OF), object=make_uri(EU), context=context)

def export_countries(format="rdf"):
    store = Store.objects.get(identifier=DEFAULT_STORE)
    graph_identifier = make_uri('http://www.wikidata.org')
    wikidata_graph = NamedGraph.objects.get(identifier=graph_identifier, store=store)
    target = "/tmp/countries.{}".format(format)
    graph = get_named_graph(make_uri('http://www.wikidata.org'))
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