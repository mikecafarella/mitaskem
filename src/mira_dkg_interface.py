import requests
import aiohttp
import asyncio

MIRA_DKG_URL = 'http://34.230.33.149:8771'


async def aget_mira_dkg_term(session, term: str,  attribs, fallback: bool, limit: int):
    fallback = str(fallback).lower()
    params = {'q': term, 'wikidata_fallback': fallback, 'limit': limit}

    async with session.get(MIRA_DKG_URL + '/api/search', params=params) as response:
        if not response.ok:
            print(f"aget_mira_dkg_term got response.ok==False for term {term}. Response: {response}")
            return [[]]
        else:
            rjson = await response.json()  # TODO does this __need__ to be awaited?
            print(f"aget_mira_dkg_term got response.json() for term {term}. Response: {rjson}")
            return [[t[attrib] for attrib in attribs if t[attrib] is not None] for t in rjson]

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
    print(f"abatch_get_mira_dkg_term: {terms}")
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









    


