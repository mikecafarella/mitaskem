import pandas as pd 
from langchain.retrievers import TFIDFRetriever
from langchain.schema import Document
from pathlib import Path
import time

def make_name_doc(tup):
    (name_str, synonym_string) = tup
    if synonym_string == '':
        syns = []
    else:
        syns = synonym_string.split(';')

    if name_str == '':
        name = []
    else:
        name = [name_str]

    keywords = name + syns    
    doc = ';'.join(keywords)
    return doc

def make_desc_doc(tup):
    (name_doc, name_desc) = tup
    if name_doc != '' and name_desc != '':
        return f'{name_doc}: {name_desc}'
    elif name_doc != '':
        return name_doc
    elif name_desc != '':
        return name_desc
    else:
        return ''


import os
from mitaskem.globals import CACHE_BASE
import requests
import pandas as pd

def build_node_retriever(df, limit) -> TFIDFRetriever:
    print(f'building index for KG ')
    df = df.rename({'name:string':'name', 'synonyms:string[]':'synonyms', 'id:ID':'id', 
                    'description:string':'description', 'type:string':'type'}, axis=1)
    df = df.assign(**(df[['name', 'synonyms', 'description']].fillna('')))

    df = df.assign(name_doc = df[['name', 'synonyms']].apply(tuple, axis=1).map(make_name_doc))
    df = df.assign(desc_doc = df[['name_doc', 'description']].apply(tuple, axis=1).map(make_desc_doc))
    cleandf = df[~(df.desc_doc == '')]

    docs = cleandf['desc_doc'].values.tolist()
    metas = cleandf[['name', 'synonyms', 'id', 'description', 'type']].apply(dict, axis=1).values.tolist()
    as_docs = [Document(page_content=doc_search, metadata=meta) for (doc_search, meta) in zip(docs, metas)]
    retriever = TFIDFRetriever.from_documents(as_docs, k=limit)
    print('done building index')
    return retriever

KG_BASE= f'{str(CACHE_BASE)}/kgs/'

_g_node_path = {
    'epi':'https://askem-mira.s3.amazonaws.com/dkg/epi/build/2023-07-07/nodes.tsv.gz',
    'climate':'https://askem-mira.s3.amazonaws.com/dkg/climate/build/2023-10-19/nodes.tsv.gz'
}

def _get_kg(kg_domain) -> pd.DataFrame:
    assert kg_domain in _g_node_path.keys()

    base = f'{KG_BASE}/{kg_domain}'
    if not os.path.exists(base):
        os.makedirs(base, exist_ok=True)

    if not os.path.exists(os.path.expanduser(f'{base}/nodes.tsv.gz')):
        url = _g_node_path[kg_domain]
        print(f'downloading kg graph {url=}')

        response = requests.get(url)
        with open(os.path.expanduser(f'{base}/nodes.tsv.gz'), 'wb') as f:
            f.write(response.content)

        print('done downloading kg graph')

    tab = pd.read_csv(os.path.expanduser(f'{base}/nodes.tsv.gz'), sep='\t', compression='gzip')
    return tab


_g_retriever_cache : dict[str,TFIDFRetriever] = {
    'epi': None,
    'climate': None
}

def _get_retriever(kg_domain) -> TFIDFRetriever:
    ''' initializes and caches retriever from kg nodes file
        use this instead of the global variable directly
    '''
    global _g_retriever_cache
    base =  f'{KG_BASE}/{kg_domain}/'
    retriever_filename = 'retriever'

    if _g_retriever_cache.get(kg_domain) is None:
        cache_file = Path(f'{base}/{retriever_filename}.joblib')

        if cache_file.exists():
            print('loading retriever from disk cache')
            start = time.time()
            _g_retriever_cache[kg_domain] = TFIDFRetriever.load_local(base, retriever_filename)
            print(f'done loading retriever from disk cache, {time.time() - start=}')
        else:
            print('building retriever from scratch')
            start = time.time()
            df = _get_kg(kg_domain=kg_domain)
            ret = build_node_retriever(df, limit=4)
            ret.save_local(base, retriever_filename)
            _g_retriever_cache[kg_domain] = ret
            print('done building retriever')

        assert cache_file.exists()

    assert _g_retriever_cache.get(kg_domain) is not None
    return _g_retriever_cache.get(kg_domain)

from typing import List
def local_batch_get_mira_dkg_term(term_list : List[str], kg_domain : str) -> List[dict]:
    batch_ans = []
    retriever : TFIDFRetriever = _get_retriever(kg_domain=kg_domain)
    for term in term_list:
        docs = retriever.get_relevant_documents(term)
        ansdocs = []
        for doc in docs:
            meta = {}
            meta.update(doc.metadata)
            ansdocs.append(meta)

        batch_ans.append(ansdocs)

    return batch_ans