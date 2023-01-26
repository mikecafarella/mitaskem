import requests


MIRA_DKG_URL = 'http://34.230.33.149:8771'


def get_mira_dkg_term(term, attribs):
    res = requests.get(MIRA_DKG_URL + '/api/search', params={'q': term})
    res = [[t[attrib] for attrib in attribs if t[attrib] is not None] for t in res.json()]
    return res

def build_local_ontology(terms, attribs):
    local_ontology = {
        term: get_mira_dkg_term(term, attribs) for term in terms
    }
    return local_ontology









    


