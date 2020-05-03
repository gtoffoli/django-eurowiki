import time
import json
import pprint
from wikidata.client import Client
from SPARQLWrapper import SPARQLWrapper, JSON

wd = 'http://www.wikidata.org/entity/'
wikidata_sparql_endpoint = 'https://query.wikidata.org/sparql'

SLEEP_TIME = 10 # seconds

EU = 'Q458'
MEMBER_OF = 'P463'
NATIONAL_ANTHEM = 'Q23691'
HAS_NATIONAL_ANTHEM = 'P85'
OF = 'P642'
NATIONAL_FLAG = 'Q186516'
MONUMENT = 'Q4989906'
NATIONAL_SYMBOL = 'Q1128637'
NATIONAL_DAY = 'Q57598'
NATIONAL_MOTTO = 'Q29654714'
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

# get the entities belonging to the EU with a sparql query
# from the User Manual: WDQS understands many shortcut abbreviations, known as prefixes. Some are internal to Wikidata,
# e.g. wd, wdt, p, ps, bd, and many others are commonly used external prefixes, like rdf, skos, owl, schema.
# see also: https://towardsdatascience.com/where-do-mayors-come-from-querying-wikidata-with-python-and-sparql-91f3c0af22e2
# TODO: remove UK; remove Netherlands or Kingdom of Netherlands
def sparql_eu_countries():
    sparql = SPARQLWrapper(wikidata_sparql_endpoint)
    sparql.setQuery("""
        SELECT ?countryLabel ?anthemLabel ?anthem_text_authorLabel ?anthem_music_authorLabel WHERE
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

"""
pp = pprint.PrettyPrinter(indent=2, compact=True)
eucc = sparql_eu_countries()
pp.pprint(eucc)

        SELECT ?countryLabel ?anthemLabel ?anthem_text_authorLabel ?anthem_music_authorLabel WHERE
        {
            ?country wdt:P463 wd:Q458 .
            ?country wdt:P85 ?anthem .
            OPTIONAL { ?anthem wdt:P676 ?anthem_text_author . }
            OPTIONAL { ?anthem wdt:P86 ?anthem_music_author . }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
        }
        ORDER BY ASC(?countryLabel)
"""