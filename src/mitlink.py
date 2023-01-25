import argparse
import json
import os.path
import uuid
import gromet_interface
import xdd_interface

MIT_KEY = "81622ba9-b82d-4128-8eb3-bec123d03979"
def get_path_from_key(key):
    file = f"{key}--Gromet-FN-auto.json"
    return file

def get_key_from_path(path):
    key = path.rsplit("/")[-1].rsplit("--")[0]
    return key
def parse_key_from_xdd_msg(json_obj):
    js = json.loads(json_obj)
    if "success" not in js:
        raise Exception("Upload to XDD failed"+ json_obj)
    return js['success']['success']['registered_ids'][0]

def parse_gromet_from_xdd(js):
    if "success" not in js:
        raise Exception("Get file from XDD failed"+ js)
    return js['success']['data'][0]

def upload_gromet_path(path):
    f = open(path)
    data = json.load(f)
    json_obj = test_xdd.put(data, MIT_KEY)
    msg = json.dumps(json_obj)
    print("Result of PUT: " + msg)
    return parse_key_from_xdd_msg(msg)


def upload_gromet_json(jsonobj):
    msg_json = test_xdd.put(jsonobj, MIT_KEY)
    msg = json.dumps(msg_json)
    return parse_key_from_xdd_msg(msg)

def get_xdd_cache(key):
    js = test_xdd.get(key)
    gromet = parse_gromet_from_xdd(js)
    print(type(gromet))
    path = get_path_from_key(key)
    f = open(path, "w")
    json.dump(gromet, f)
    f.close()
    return path

def annotate_cache_upadte(key, att, value):
    # pull key from xdd and cache locally if not exist
    path = get_path_from_key(key)
    if os.path.exists(path) == False:
        path = get_xdd_cache(key)
        print("Get gromet file with key " + key + " from xdd and cache to local\n" + path)
    else:
        print(path + " exist in local file\n")

    # extract parent key
    source = get_key_from_path(path)
    # generate currnet key
    # newkey = str(uuid.uuid4())
    # newpath = get_path_from_key(newkey)

    # read from local file
    f = open(path)
    js = json.load(f)
    # print(type(js))
    f.close()
    # add trace to the source file and apply annotation
    js['source'] = source
    js[att] = value

    newkey = upload_gromet_json(js)
    newpath = get_path_from_key(newkey)
    print("annotate source gromet file " + key + " with annotation and upload to XDD with new uuid " + newkey)
    with open(newpath, "w") as outfile:
        outfile.write(json.dumps(js, indent=4))
    print("Save annotated gromet to local directory\n" + newpath)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Parse python program path (arg0) to gromet representation")
    parser.add_argument("-o", "--output_path", type=str, help="Output path for parsed gromet", default=".")
    # parser.add_argument("-p", "--put", nargs='+',
    #                     help="Uplaod gromet file path (arg0) to xDD with optional uuid (arg1), automatically generate if not provided")
    parser.add_argument("-p", "--put", nargs='+', help="Uplaod gromet file path (arg0)")

    parser.add_argument("-g", "--get", type=str, help="xDD key (arg0) for the target gromet")
    parser.add_argument("-a", "--annotate", nargs='+',
                        help="get gromet object with xDD key (arg0), update groment attribute key (arg1) with value (arg2) ")
    args = vars(parser.parse_args())

    if args["input"]:
        print("Input file is " + args["input"])
        gromet_interface.run_pipeline_export_gromet(args["input"], args["output_path"])
    elif args["put"]:
        kv = list(args["put"])
        if len(kv) == 1:
            key = upload_gromet_path( kv[0])
            print("update gromet file " + kv[0] + " with auto generated uuid " + key)
        else:
            # not supported
            key = kv[1]
            upload_gromet_path(kv[0])
            print("update gromet file " + kv[0] + " with custom uuid " + key)

    elif args["get"]:
        path = get_xdd_cache(args["get"])
        print("get gromet file with key " + args["get"] + " and save to \n" + path)
    elif args["annotate"]:
        kv = list(args["annotate"])
        key = kv[0]
        att = kv[1]
        value = kv[2]
        annotate_cache_upadte(key, att, value)


if __name__ == "__main__":
    main()
