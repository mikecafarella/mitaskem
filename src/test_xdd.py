#!/usr/bin/env python3
import datetime
import requests
import json

XDD_CREATE_URL = "https://xdddev.chtc.io/askem/create"
XDD_GET_URL = "https://xdddev.chtc.io/askem/object/"
MIT_KEY = "81622ba9-b82d-4128-8eb3-bec123d03979"
    
def get(reqid):
    r = requests.get(XDD_GET_URL + reqid)
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("XDD GET failed")
    

def put(jsonObj, key):
    if "data" not in jsonObj:
        raise Exception("Cannot create XDD object without 'data' field")
    if "metadata" not in jsonObj:
        raise Exception("Cannot create XDD object without 'metadata' field")


    # HEADERS
    # "x-api-key" should be KEY
    # "Content-type: application/json"
    r = requests.post(XDD_CREATE_URL,
                      headers={"x-api-key": key,
                               "Content-Type": "application/json"},
                      data=json.dumps(jsonObj))

    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("XDD POST failed")


if __name__ == "__main__":
    objid = "b3669d32-d422-49c7-ad0b-becf1e2bc0b0"

    # TEST PUT
    testObj = {"data": "xyz",
              "metadata": {
                "documents": {
                 "key1": {
                   "title": "Some Fake Thing"
                 }
               }
             }
           }

    print("Result of PUT: " + str(put(testObj, MIT_KEY)))

    # Test GET

    print("RESULT OF GET: " + str(get(objid)))

