import pandas as pd
# from rdflib.term import URIRef, BNode, Literal
from rdflib_django.utils import get_conjunctive_graph
from .classes import Country, make_item


from django.conf import settings
wdt = settings.RDF_PREFIXES['wdt']
national_anthem = '{}{}'.format(wdt, 'P85')
music_composer = '{}{}'.format(wdt, 'P86')
text_author = '{}{}'.format(wdt, 'P676')

queries = {
    'anthems': {
        'title': 'National anthems by country, with music composer and text author',
        'sparql': """
SELECT ?country ?anthem ?composer ?author
       WHERE {
          ?country wdt:P85 ?anthem .
          OPTIONAL { ?anthem wdt:P86 ?composer } .
          OPTIONAL { ?anthem wdt:P676 ?author } .
       }
""",},
}

def run_query(query, g=None):
    if not g:
        g = get_conjunctive_graph()
    # query = queries[key]['sparql']
    print(query)
    query_result = g.query(query)
    return query_result

def print_qres(qres):
    for row in qres:
        print(row)

def query_result_to_dataframe(query_result):
    bindings = query_result.bindings
    # columns = [var.toPython().replace('?','') for var in bindings[0].keys()]
    columns = [var.toPython().replace('?','') for var in bindings[0]]
    data = []
    for row in query_result:
        els = []
        for term in row:
            item = make_item(term)
            if item:
                if isinstance(item, Country):
                    els.append(item.label())
                else:
                    els.append(item.preferred_label()[0])
            else:
                els.append(term or '')
        data.append(els)
    dataframe = pd.DataFrame(data, columns=columns)
    dataframe.sort_values(columns[0], inplace=True)
    return dataframe

def dataframe_to_html(df):
    html = df.to_html(index=False, justify='center', classes='ew-table')
    return html

def dataframe_to_csv(df, sep='\t', index=False):
    txt = df.to_csv(sep=sep, index=index)
    return txt
