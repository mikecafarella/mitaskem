import argparse
import json
import os.path
import uuid
import gromet
import test_xdd

def get_path_from_key(key):
    file = f"model/{key}--Gromet-FN-auto.json"
    return file

def get_key_from_path(path):
    key = path.rsplit("/")[-1].rsplit("--")[0]
    return key

def update_gromet_path_with_key(key, path):
    f = open(path)
    data = f.read()
    print("Result of PUT: " + str(test_xdd.put(data, key)))

def get_xdd_cache(key):
    js = str(test_xdd.get(key))
    print(js)
    path = get_path_from_key(key)
    f = open(path, "w")
    f.write(js)
    f.close()
    return path

def annotate_cache_upadte(key, att, value):
    # pull key from xdd and cache locally if not exist
    path = get_path_from_key(key)
    if os.path.exists(path) == False:
        get_xdd_cache(key)
        print("Get gromet file with key " + key + " from xdd and cache to local\n" + path)
    else:
        print(path + " exist in local file\n")

    # extract parent key
    source = get_key_from_path(path)
    # generate currnet key
    newkey = str(uuid.uuid4())
    newpath = get_path_from_key(newkey)

    # read from local file
    f = open(path)
    js = json.load(f)
    f.close()
    # add trace to the source file and apply annotation
    js['source'] = source
    js[att] = value

    json_str = json.dumps(js)
    with open(newpath, "w") as outfile:
        outfile.write(json_str)
    print("Annotate gromet file with key " + key + " and save to \n" + newpath)
    update_gromet_path_with_key(newkey, newpath)
    print("Update new gromet file " + newpath + " with custom uuid " + newkey)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Parse python program path (arg0) to gromet representation")
    parser.add_argument("-p", "--put", nargs='+',
                        help="Uplaod gromet file path (arg0) to xDD with optional uuid (arg1), automatically generate if not provided")
    parser.add_argument("-g", "--get", type=str, help="xDD key (arg0) for the target gromet")
    parser.add_argument("-a", "--annotate", nargs='+',
                        help="get gromet object with xDD key (arg0), update groment attribute key (arg1) with value (arg2) ")
    args = vars(parser.parse_args())

    if args["input"]:
        print("Input file is " + args["input"])
        gromet.run_pipeline_export_gromet(args["input"])
    elif args["put"]:
        kv = list(args["put"])
        if len(kv) == 1:
            key = str(uuid.uuid4())
            update_gromet_path_with_key(key, kv[0])
            print("update gromet file " + kv[0] + " with auto generated uuid " + key)
        else:
            key = kv[1]
            update_gromet_path_with_key(key, kv[0])
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
