import pandas as pd
# from rdflib.term import URIRef, BNode, Literal
from rdflib_django.utils import get_conjunctive_graph
from .classes import Country, make_item


def run_query(query, g=None):
    if not g:
        g = get_conjunctive_graph()
    query_result = g.query(query)
    return query_result

# def query_result_to_dataframe(query_result):
def query_result_to_dataframe(query_result, columns=None):

    if not columns:
        bindings = query_result.bindings
        """
        20201012 MMR
        columns = [var.toPython().replace('?','') for var in bindings[0]]
        """
        columns = []
        for var in bindings:
            for v in var:
                el=v.toPython().replace('?','')
                if not (el in columns):
                    columns.append(el)
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
    if data:
        dataframe.sort_values(columns[0], inplace=True)
    return dataframe

def dataframe_to_html(df):
    pd.set_option('display.max_colwidth', -1)
    df = df.replace(r'\r\n','<br />', regex=True)
    html = df.to_html(index=False, border="0", justify='left', classes='table ew-table-results', escape=False, render_links=True)
    return html

def dataframe_to_csv(df, sep='\t', index=False):
    txt = df.to_csv(sep=sep, index=index)
    return txt

def get_query_variables(query):
    tokens = query.split()
    variables = []
    select = False
    coalesce = 0
    for token in tokens:
        if token.lower() == 'select':
            select = True
            continue
        elif token.lower() == 'where':
            break
        elif token.lower() == 'coalesce':
            coalesce = 1
        elif coalesce and token == '(':
            coalesce += 1
        elif coalesce == 2 and token == ')':
            coalesce = 0
        elif select and not coalesce and token.startswith('?'):
            variables.append(token.replace('?',''))
    return variables