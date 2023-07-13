import requests
import aiohttp
import asyncio
import json

MIRA_DKG_URL = 'http://34.230.33.149:8771'


async def aget_mira_dkg_term(session, term,  attribs, fallback, limit):
    json_params = json.dumps({'q': term, 'wikidata_fallback': fallback, 'limit': limit})

    async with session.get(MIRA_DKG_URL + '/api/search', params=json_params) as response:
        if not response.ok:
            return [[]]
        else:
            async with response.json() as rjson:
                return  [[t[attrib] for attrib in attribs if t[attrib] is not None] for t in rjson]


def get_mira_dkg_term(term, attribs, fallback=False, limit=5):
    params = {'q': term, 'wikidata_fallback': fallback, 'limit': limit}
    res = requests.get(MIRA_DKG_URL + '/api/search', params=params)
    # handle dkg error
    if not res.ok:
        return [[]]
    res = [[t[attrib] for attrib in attribs if t[attrib] is not None] for t in res.json()]
    return res          

def batch_get_mira_dkg_term(terms, attribs, fallback=False, limit=5):
    res = []
    for term in terms:
        res.append(get_mira_dkg_term(term, attribs, fallback, limit))
    return res

async def abatch_get_mira_dkg_term(terms, attribs, fallback=False, limit=5):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for term in terms:
            cor = aget_mira_dkg_term(session,term, attribs, fallback, limit)
            tasks.append(asyncio.create_task(cor))


        ans = []
        for task in tasks:
            ans.append(await task)

    return ans


def build_local_ontology(terms, attribs):
    local_ontology = {
        term: get_mira_dkg_term(term, attribs) for term in terms
    }
    return local_ontology









    


