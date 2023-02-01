
import argparse
import json
import unicodedata as ud


def main(args):

    out_filename = args.out_dir + "/" + args.anno_path.split("/")[-1].split(".")[0] + "_annotations_dict.json"

    # Get inputs
    jsonFile1 = open(args.pyacset_path, 'r')
    pyacset = json.load(jsonFile1)
    jsonFile1.close()

    jsonFile2 = open(args.anno_path, 'r')
    annos = json.load(jsonFile2)
    jsonFile2.close()

    # Build dictionary of variables
    var_d = {}
    for anno in annos:
        if anno["type"] != "variable":
            continue
        var_d[anno["name"]] = anno

    d = {}

    # Process states
    states = pyacset["S"]
    for state in states:
        name = state["sname"].lstrip().rstrip()
        uid = state["uid"]
        d[uid] = var_d.get(name, {})

    # Process transitions
    transitions = pyacset["T"]
    for tr in transitions:
        name = tr["tname"].lstrip().rstrip()
        uid = tr["uid"]

        d[uid] = var_d.get(ud.lookup(f"GREEK SMALL LETTER {name.upper()}"), {})

    # Write out
    with open(out_filename, "w") as f:
        json.dump(d, f)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pyacset_path", type=str)
    parser.add_argument("-a", "--anno_path", type=str)
    parser.add_argument("-o", "--out_dir", type=str)
    args = parser.parse_args()

    main(args)