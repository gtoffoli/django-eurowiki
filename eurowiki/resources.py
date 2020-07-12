""" IN PROGRESS
This module is an extension of settings.py, to be imported by it.
It includes definitions complementing the database of rdflib_django.
Should include only terminology and the core of top-level items.
"""


DEFAULT_STORE = "http://www.eurowiki.eu"

# this dictionary should allow to derive sources from namespace prefix
WIKIDATA_BASE = 'http://www.wikidata.org'
EUROWIKI_BASE = 'http://www.eurowiki.eu'
RDF_PREFIXES = {
    "xsd": 'http://www.w3.org/2001/XMLSchema#',
    "rdf": 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    "rdfs": 'http://www.w3.org/2000/01/rdf-schema#',
    "wd": '{}/{}'.format(WIKIDATA_BASE, 'entity/'), # wikidata items
    "wdt": '{}/{}'.format(WIKIDATA_BASE, 'prop/direct/'), # wikidata property "truthy"
    "p": '{}/{}'.format(WIKIDATA_BASE, 'prop/'), # wikidata property type
    "ew": '{}/{}'.format(EUROWIKI_BASE, 'entity/'), # eurowiki items
    "ewp": '{}/{}'.format(EUROWIKI_BASE, 'prop/'), # eurowiki items
    "ewt": '{}/{}'.format(EUROWIKI_BASE, 'prop/direct/'), # eurowiki property "truthy"
}
RDF_PREFIX_ITEMS = RDF_PREFIXES.items()
# The URI RDFS_LABEL (http://www.w3.org/2000/01/rdf-schema#label) is defined explicitly here, since
# calling URIRef with the base argument (see make_uriref above) seems broken for namespaces ending with "#"
RDFS_LABEL = RDF_PREFIXES['rdfs']+'label'
RDFS_COMMENT = RDF_PREFIXES['rdfs']+'comment'
RDFS_MEMBER = RDF_PREFIXES['rdfs']+'member'
RDF_BAG =  RDF_PREFIXES['rdf']+'Bag'

URI_LABEL_CODES = {
    "wd": 'Q', # wikidata items
    "wdt": 'P', # wikidata property "truthy"
    "ew": 'QUE', # eurowiki items
    "ewt": 'PUE', # eurowiki property "truthy"
}

UNKNOWN_LABEL_DICT = {'en': '?', 'it': '?'}
EU = 'Q458'
EU_LABELS = {'en': 'European Union', 'it': 'Unione Europea'}

from collections import OrderedDict
EU_COUNTRY_LABELS = OrderedDict([
    ('Q40', {'en': 'Austria', 'it': 'Austria',}), # Austria
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
    ('Q29', {'en': 'Spain', 'it': 'Spagna',}), # Spain
    ('Q34', {'en': 'Sweden', 'it': 'Svezia',}), # Sweden
    ('Q28', {'en': 'Hungary', 'it': 'Ungheria',}), #  (member of Q458)
    ('Q145', {'en': 'United Kingdom', 'it': 'Regno Unito',}), #
])
EU_COUNTRY_KEYS = list(EU_COUNTRY_LABELS.keys())

OTHER_ITEM_LABELS = {
    'Q458': {'en': 'European Union', 'it': 'Unione Europea'},
    'Q4916': {'en': 'Euro', 'it': 'Euro'},
    'Q8886': {'en': 'European Council', 'it': 'Consiglio Europeo'}, 
    'Q3624078': {'en': 'sovereign state', 'it': 'stato sovrano',},
    'Q2065736': {'en': 'cultural property', 'it': 'bene culturale',},
    'Q4989906': {'en': 'monument', 'it': 'monumento',},
    'Q1128637': {'en': 'national symbol', 'it': 'simbolo nazionale',}, # symbol of national identity
    'Q23691': {'en': 'national anthem', 'it': 'inno nazionale',},
    'Q186516': {'en': 'national flag', 'it': 'bandiera nazionale',},
    'Q1128637': {'en': 'national symbol', 'it': 'simbolo nazionale',},
    'Q57598': {'en': 'national day', 'it': 'festa nazionale',},
    'Q29654714': {'en': 'national motto', 'it': 'motto nazionale',},
    'Q1079693': {'en': 'national emblem', 'it': 'stemma nazionale',},
    'Q7755': {'en': 'constitution', 'it': 'costituzione',},
}

PREDICATE_LABELS =  OrderedDict([
    ('label', {'en': 'name/title', 'it': 'nome/titolo',}), #
    ('P1476', {'en': 'original title', 'it': 'titolo originale',}), # original title
    ('PUE1', {'en': 'text', 'it': 'testo',}), #
    ('P953', {'en': 'online full text', 'it': 'testo completo online',}), # 'full work available at', 'testo completo disponibile all'indirizzo'
    ('PUE2', {'en': 'description', 'it': 'descrizione',}), #
    ('P18', {'en': 'image', 'it': 'immagine',}), #

    ('P85', {'en': 'national anthem', 'it': 'inno nazionale',}), # national anthem (of country)
    ('P163', {'en': 'national flag', 'it': 'bandiera nazionale',}), # 
    ('P237', {'en': 'coat of arms', 'it': 'stemma',}), # description of emblem
    ('P1546', {'en': 'national motto', 'it': 'motto nazionale',}), # motto (of country)
    ('P832', {'en': 'public holiday', 'it': 'festa nazionale',}),
    ('PUE6', {'en': 'national monument', 'it': 'monumento nazionale',}), # brand-NEW - domain: Q3624078, range: Q4989906 and Q1128637
    ('P38', {'en': 'currency and coinage', 'it': 'valuta e monetazione',}), # in wikidata: 'currency', 'valuta'
    ('P92', {'en': 'constitution', 'it': 'costituzione',}), # in wikidata: 'main regulatory text', 'legge fondamentale'

    ('P170', {'en': 'creator/author', 'it': 'creatore/autore',}),
    ('P676', {'en': 'text author', 'it': 'autore del testo',}), # text author (of lyrics)
    ('P86', {'en': 'music composer', 'it': 'compositore',}), # composer (of music)

    ('PUE3', {'en': 'proposed by', 'it': 'proposto da',}), # REPURPOSED - in WD: P748 (appointed by, designato da)
    ('P790', {'en': 'deliberated by', 'it': 'deliberato da',}), # in wikidata: approved by, approvato da (ente)
    ('P828', {'en': 'grounds for the adoption', 'it': "motivazione per l'adozione",}), # in wikidata: 'has cause', 'causato da'
    ('PUE8', {'en': 'year or time of composition or adoption', 'it': 'anno o circostanze di composizione o adozione',}), # brand-new
    ('P571', {'en': 'adoption date', 'it': 'data di adozione',}), # in wikidata: 'inception, data di fondazione o creazione'
    ('P580', {'en': 'start date', 'it': 'data di inizio',}), # start time (of validity of a property assertion)
    ('PUE4', {'en': 'historical origins', 'it': 'origini storiche',}), # brand-NEW
    ('PUE5', {'en': 'cultural significance', 'it': 'significato culturale',}), # brand-NEW
    ('PUE9', {'en': 'changes since origin or adoption', 'it': 'modifiche da origine o adozione',}), # brand-new

    ('PUE7', {'en': 'subjects depicted', 'it': 'soggetti raffigurati',}), # multi-value shortcut for a relation path involving P180
    ('P547', {'en': 'commemorates', 'it': 'commemora',}), # 
    ('P837', {'en': 'day of year', 'it': 'giorno di ricorrenza',}), # "day in year for periodic occurrence"
    ('PUE15', {'en': 'commemorative coins', 'it': 'monete commemorative',}), # brand-NEW for currency and coinage
    ('PUE16', {'en': 'celebration mode', 'it': 'modalità di celebrazione',}), # brand-NEW for holidays
    ('PUE17', {'en': 'possible variations', 'it': 'possibili varianti',}), # brand-NEW for many symbols

    ('PUE11', {'en': 'general principles', 'it': 'principi generali',}), # brand-NEW for constitutions
    ('PUE12', {'en': 'soverainity cession', 'it': 'cessione di sovranità',}), # brand-NEW for constitutions
    ('PUE13', {'en': 'mentions to religions', 'it': 'riferimenti alla religione',}), # brand-NEW for constitutions
    ('PUE14', {'en': 'human rights and minorities', 'it': 'diritti umani e minoranze',}), # brand-NEW for constitutions

    ('P854', {'en': 'online reference', 'it': 'riferimento online',}),
    ('P248', {'en': 'source', 'it': 'fonte',}), # (statement) source, fonte (dell'affermazione)
    ('P948', {'en': 'page banner', 'it': 'banner di pagina',}), #
    ('comment', {'en': 'comment', 'it': 'commento',}), #
])

CURRENTLY_HIDDEN_PREDICATE_LABELS =  OrderedDict([
    ('P242', {'en': 'stated in', 'it': "fonte dell'affermazione",}), # applies only to statements
    ('P31', {'en': 'instance of', 'it': 'istanza di',}), # instance of
    ('P279', {'en': 'subclass of', 'it': 'sottoclasse di',}), # subclass of

    ('P361', {'en': 'Part of', 'it': 'Parte di',}), # part of
    ('P463', {'en': 'member of', 'it': 'membro di',}), # member of
    ('P17', {'en': 'country', 'it': 'paese',}), # country
    ('P495', {'en': 'country of origin', 'it': 'paese di origine',}), # country of origin
    ('P642', {'en': 'refers to', 'it': 'relativo a',}), # of (refers to)
    ('P144', {'en': 'based on', 'it': 'basato su',}), # 'opere usate come base per il soggetto'
    ('P180', {'en': 'depicts', 'it': 'raffigura',}), #
    ('PUE10', {'en': 'national day', 'it': 'festa nazionale',}), # brand-new (usually one among public holidays)

    ('P41', {'en': 'flag image', 'it': 'immagine della bandiera',}), #
    ('P94', {'en': 'emblem image', 'it': 'immagine dello stemma',}), #

    ('P2441', {'en': 'literal translation', 'it': 'traduzione letterale',}),
    ('P1541', {'en': 'motto text', 'it': 'testo del motto',}), # motto text (of country)
    ('P577', {'en': 'publication date', 'it': 'data di pubblicazione',}),
    ('P582', {'en': 'end date', 'it': 'data di fine',}), # end time (of validity of a property assertion)
])

"""
EW_PREDICATE_LABELS = OrderedDict([
])
PREDICATE_LABELS.update(EW_PREDICATE_LABELS)
"""
ORDERED_PREDICATE_KEYS = list(PREDICATE_LABELS.keys())

EU_COUNTRY_PROPERTIES = ['P85', 'P163', 'P237', 'P1546', 'PUE6', 'P832', 'P38', 'P92',] # mandatory 1st level properties for countries
LITERAL_PROPERTIES = ['label', 'PUE1', 'PUE2', 'P41', 'P94', 'P1541', 'P1476', 'P18', 'P828', 'P571', 'P577', 'P580', 'P582', 'P837', 'P948', 'P953', 'P854', 'PUE4', 'PUE5', 'PUE7', 'PUE8', 'PUE9', 'PUE11', 'PUE12', 'PUE13', 'PUE14', 'PUE15', 'PUE16', 'PUE17', 'comment', 'P248',] # properties occurring in Literal Statements
RDF_I18N_PROPERTIES = ['label', 'PUE1', 'PUE2', 'P1541', 'P1476', 'P828', 'P837', 'PUE4', 'PUE5', 'PUE7', 'PUE8', 'PUE9', 'PUE11', 'PUE12', 'PUE13', 'PUE14', 'PUE15', 'PUE16', 'PUE17', 'comment',] # RDF properties having a literal value language-awware
IMAGE_PROPERTIES = ['P18', 'P41', 'P94', 'P948',] # properties from whose value an online address can be computed 
URL_PROPERTIES = ['P854', 'P953',]
REPEATABLE_PROPERTIES = ['PUE6', 'P832',] # predicates allowing multiple properties for same subject 

# this sample dictionary should allow to compute URIs, based on prefix to namespace mapping
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

EW_TREE = OrderedDict([
    ('P85', ('P1476', 'PUE1', 'PUE2', 'PUE17', 'P953', 'P676', 'P86', 'P790', 'PUE4', 'PUE8', 'P571', 'P828','PUE9', 'P854', 'P248', 'comment',),), # national anthem: title, text auth., composer, ...
    ('P163', ('P18', 'PUE2', 'PUE17', 'PUE3', 'P790', 'PUE4', 'PUE5', 'PUE8', 'P571', 'P828', 'PUE9', 'P854', 'P248', 'comment',),), # national flag: descr., img, prop., delib., date, ...
    ('P237', ('P18', 'PUE2', 'PUE17', 'P170', 'PUE3', 'P790', 'PUE4', 'PUE5', 'PUE8', 'P571', 'P828','PUE9', 'P854', 'P248', 'comment',),), # national emblem: descr., img, prop., delib., date, ...
    ('P1546', ('P1541', 'PUE2', 'PUE17', 'PUE3', 'P790', 'PUE4', 'PUE5', 'PUE8', 'P571', 'P828','PUE9', 'P854', 'P248', 'comment',),), #national motto: text
    ('PUE6', ('PUE2', 'P170', 'PUE3', 'P790', 'PUE4', 'PUE5', 'PUE8', 'P571', 'P828','PUE9', 'P854', 'P248', 'comment',),), # national monuments
    ('P832', ('PUE1', 'PUE2', 'PUE17', 'P837', 'PUE16', 'PUE4', 'PUE5', 'PUE3', 'P790', 'PUE8', 'P571', 'P828','PUE9', 'P854', 'P248', 'comment',),), # national (holi)days: title, day,  prop., delib., date, ...
    ('P38', ('PUE2', 'PUE3', 'P790', 'P571', 'PUE4', 'P828', 'PUE7', 'PUE8','PUE9', 'P854', 'P248', 'PUE15', 'comment',),), # currency and coinage
    ('P92', ('P953', 'PUE2', 'PUE3', 'P790', 'PUE4', 'PUE5', 'PUE8', 'P571', 'PUE9', 'PUE11', 'PUE12',  'PUE13', 'PUE14', 'P854', 'P248', 'comment',),), # national constitution
    # ('Bag', ('', 'P832',),), # container of members (monuments and days)
])
EW_TREE_KEYS = list(EW_TREE.keys())

EW_SUBTREE = OrderedDict([
    ('P170',('PUE2', 'comment')),
    ('P676',('PUE2', 'comment')),
    ('P86',('PUE2', 'comment')),
    ('P790',('PUE2', 'comment')),
    ('PUE3',('PUE2', 'comment')),
    ('P547',('PUE2', 'comment')),
])

EW_SUBTREE_KEYS = list(EW_SUBTREE.keys())

LITERAL_LEAF_KEYS = ('label', 'PUE2', 'P854', 'P248', 'comment',)

EURO_LANGUAGES = (
    ('en', 'English'),
    ('it', 'Italiano'),
    ('de', 'German'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('bg', 'Bulgarian'),
    ('cs', 'Czech'),
    ('da', 'Danish'),
    ('el', 'Greek'),
    ('et', 'Estonian'),
    ('fi', 'Finnish'),
    ('ga', 'Irish'),
    ('hr', 'Croatian'),
    ('hu', 'Hungarian'),
    ('lt', 'Lithuanian'),
    ('lv', 'Latvian'),
    ('mt', 'Maltese'),
    ('nl', 'Dutch'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese'),
    ('ro', 'Romanian'),
    ('sk', 'Slovak'),
    ('sl', 'Slovenian'),
    ('sv', 'Swedish'),
)
EURO_LANGUAGE_CODES = [l[0] for l in EURO_LANGUAGES]
