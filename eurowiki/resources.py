""" IN PROGRESS
This module is an extension of settings.py, to be imported by it.
It includes definitions complementing the database of rdflib_django.
Should include only terminology and the core of top-level items.
"""

# this dictionary should allow to derive sources from namespace prefix
EXTERNAL_SOURCES = {
  "wikidata": [
    "wd", # wikidata items
    "p", # wikidata property types
  ],
}

# this dictionary should allow to compute URIs, based on prefix to namespace mapping
EXTERNAL_RESOURCES = {
  "wd": [
    'Q205892', # calendar date
    'Q6256', # country
    'Q4989906', # monument
    'Q811979', # architectural structure

    'Q1128637', # national symbol
    'Q7148059', # patriotic song
    'Q186516', # national flag (subclass of Q1128637)
    'Q23691', # national anthem (subclass of Q1128637 and of Q7148059)
    'Q57598', # national day (subclass of Q1128637 and Q205892)
    'Q29654714', # national motto (subclass of Q1128637)

    'Q458', # European Union

    'Q28', # Hungary (member of Q458)
    'Q29', # Spain
    'Q31', # Belgium
    'Q32', # Luxembourg
    'Q33', # Finland
    'Q34', # Sweden
    'Q35', # Denmark
    'Q36', # Poland
    'Q37', # Lithuania
    'Q38', # Italy
    'Q40', # Austria
    'Q41', # Greece
    'Q45', # Portugal
    'Q142', # France
    'Q183', # Germany
    'Q191', # Estonia
    'Q211', # Latvia
    'Q213', # Czech Republic
    'Q214', # Slovakia
    'Q215', # Slovenia
    'Q218', # Romania
    'Q219', # Bulgaria
    'Q224', # Croatia
    'Q229', # Republic of Cyprus
    'Q233', # Malta
    'Q22890', # Ireland
    'Q29999', # Netherlands

    # some examples:
    'Q187', # Inno di Mameli (instance of Q23691, of Q38)
    'Q41180', # La Marseillaise (instance of Q23691, - P642 Q142)
    'Q326724', # Bastille Day (instance of Q57598, - P17 Q142)
    'Q506234', # Altare della Patria (instance of Q4989906 and Q1128637, - P17 Q38)
  ],
  "p": [
    'P279', # subclass of
    'P31', # instance of
    'P361', # part of

    'P463', # member of

    'P17', # country
    'P642', # of (refers to)
    'P86', # composer (its music author)
    'P676', # lyrics by (its text author)
    'P495', # country of origin

    'P580', # start time (of validity of a property assertion)
    'P582', # end time (of validity of a property assertion)


  ]
  
}
