""" IN PROGRESS
This module is an extension of settings.py, to be imported by it.
It includes definitions complementing the database of rdflib_django.
Should include only terminology and the core of top-level items.
"""

# this dictionary should allow to derive sources from namespace prefix
WIKIDATA_BASE = 'http://www.wikidata.org'
RDF_PREFIXES = {
    "rdfs": 'http://www.w3.org/2000/01/rdf-schema#',
    "wd": '{}/{}'.format(WIKIDATA_BASE, 'entity/'), # wikidata items
    "wdt": '{}/{}'.format(WIKIDATA_BASE, 'prop/direct/'), # wikidata property "truthy"
    "p": '{}/{}'.format(WIKIDATA_BASE, 'prop/'), # wikidata property type
}
RDF_PREFIX_ITEMS = RDF_PREFIXES.items()

EU = 'Q458'
EU_LABELS = {'en': 'European Union', 'it': 'Unione Europea'}

from collections import OrderedDict
EU_COUNTRY_LABELS = OrderedDict([
    ('Q40', {'en': 'Austria', 'it': 'Austria',}), # Austria
    ('Q29', {'en': 'Spain', 'it': 'Spagna',}), # Spain
    ('Q31', {'en': 'Belgium', 'it': 'Belgio',}), # Belgium
    ('Q219', {'en': 'Bulgaria', 'it': 'Bulgaria',}), # Bulgaria
    ('Q224', {'en': 'Croatia', 'it': 'Croazia',}), # Croatia
    ('Q229', {'en': 'Republic of Cyprus', 'it': 'Cipro',}), # Republic of Cyprus
    ('Q213', {'en': 'Czech Republic', 'it': 'Repubblica Ceca',}), # Czech Republic
    ('Q35', {'en': 'Denmark', 'it': 'Danimarca',}), # Denmark
    ('Q191', {'en': 'Estonia', 'it': 'Estonia',}), # Estonia
    ('Q33', {'en': 'Finland', 'it': 'Finlandia',}), # Finland
    ('Q142', {'en': 'France', 'it': 'Francia',}), # France
    ('Q183', {'en': 'Germany', 'it': 'Germania',}), # Germany
    ('Q41', {'en': 'Greece', 'it': 'Grecia',}), # Greece
    ('Q27', {'en': 'Ireland', 'it': 'Irlanda',}), # Ireland
    ('Q38', {'en': 'Italy', 'it': 'Italia',}), # Italy
    ('Q211', {'en': 'Latvia', 'it': 'Lettonia',}), # Latvia
    ('Q37', {'en': 'Lithuania', 'it': 'Lituania',}), # Lithuania
    ('Q32', {'en': 'Luxembourg', 'it': 'Lussemburgo',}), # Luxembourg
    ('Q233', {'en': 'Malta', 'it': 'Malta',}), # Malta
    ('Q55', {'en': 'Netherlands', 'it': 'Paesi Bassi',}), # Netherlands
    ('Q29999', {'en': 'Kingdom of Netherlands', 'it': 'Paesi Bassi',}), # Kingdom of Netherlands
    ('Q36', {'en': 'Poland', 'it': 'Polonia',}), # Poland
    ('Q45', {'en': 'Portugal', 'it': 'Portogallo',}), # Portugal
    ('Q218', {'en': 'Romania', 'it': 'Romania',}), # Romania
    ('Q214', {'en': 'Slovakia', 'it': 'Slovacchia',}), # Slovakia
    ('Q215', {'en': 'Slovenia', 'it': 'Slovenia',}), # Slovenia
    ('Q34', {'en': 'Sweden', 'it': 'Svezia',}), # Sweden
    ('Q28', {'en': 'Hungary', 'it': 'Ungheria',}), #  (member of Q458)
    ('Q145', {'en': 'United Kingdom', 'it': 'Regno Unito',}), #
])

OTHER_ITEM_LABELS = {
    'Q458': {'en': 'European Union', 'it': 'Unione Europea'},
    'Q3624078': {'en': 'sovereign state', 'it': 'stato sovrano',},
    'Q23691': {'en': 'national anthem', 'it': 'inno nazionale',},
    'Q186516': {'en': 'national flag', 'it': 'bandiera nazionale',},
    'Q1128637': {'en': 'national symbol', 'it': 'simbolo nazionale',},
    'Q57598': {'en': 'national day', 'it': 'festa nazionale',},
    'Q29654714': {'en': 'national motto', 'it': 'motto nazionale',},
    'Q1079693': {'en': 'national emblem', 'it': 'stemma nazionale',},
}

PREDICATE_LABELS =  OrderedDict([
    ('label', {'en': 'label', 'it': 'etichetta',}), #
    ('P279', {'en': 'subclass of', 'it': 'sottoclasse di',}), # subclass of
    ('P31', {'en': 'instance of', 'it': 'istanza di',}), # instance of
    ('P361', {'en': 'Part of', 'it': 'Parte di',}), # part of
    ('P463', {'en': 'member of', 'it': 'membro di',}), # member of
    ('P17', {'en': 'country', 'it': 'paese',}), # country
    ('P642', {'en': 'refers to', 'it': 'relativo a',}), # of (refers to)

    ('P85', {'en': 'national anthem', 'it': 'inno nazionale',}), # national anthem (of country)
    ('P163', {'en': 'national flag', 'it': 'bandiera nazionale',}), # 
    ('P237', {'en': 'coat of arms', 'it': 'descrizione dello stemma',}), # description of emblem
    ('P1541', {'en': 'motto text', 'it': 'testo del motto',}), # motto text (of country)
    ('P1546', {'en': 'national motto', 'it': 'motto nazionale',}), # motto (of country)
    ('P832', {'en': 'public holiday', 'it': 'festa nazionale',}),
    ('P1476', {'en': 'title', 'it': 'titolo',}), # 
    ('P86', {'en': 'music composer', 'it': 'compositore',}), # composer (of music)
    ('P676', {'en': 'text author', 'it': 'autore del testo',}), # text author (of lyrics)

    ('P495', {'en': 'country of origin', 'it': 'paese di origine',}), # country of origin
    ('P580', {'en': 'start date', 'it': 'data di inizio',}), # start time (of validity of a property assertion)
    ('P582', {'en': 'end date', 'it': 'data di fine',}), # end time (of validity of a property assertion)
])
ORDERED_PREDICATE_KEYS = list(PREDICATE_LABELS.keys())

EU_COUNTRY_PROPERTIES = ['P163', 'P85', 'P237', 'P1546',]

# this dictionary should allow to compute URIs, based on prefix to namespace mapping
OTHER_EXTERNAL_RESOURCES = {
  "wd": [
    # miscellaneous concepts
    'Q205892', # calendar date
    'Q6256', # country
    'Q4989906', # monument
    'Q811979', # architectural structure
    'Q7148059', # patriotic song
    # some instances:
    'Q187', # Inno di Mameli (instance of Q23691, of Q38)
    'Q41180', # La Marseillaise (instance of Q23691, - P642 Q142)
    'Q326724', # Bastille Day (instance of Q57598, - P17 Q142)
    'Q506234', # Altare della Patria (instance of Q4989906 and Q1128637, - P17 Q38)
  ],
}
