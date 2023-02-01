
import argparse
import json
import unicodedata as ud
import ast


def link_annos_to_pyacset(pyacset_s, annos_s, info_s=""):
    pyacset = ast.literal_eval(pyacset_s)
    annos = ast.literal_eval(annos_s)
    if info_s != "":
        info = ast.literal_eval(info_s)

    # Build dictionary of variables
    var_d = {}
    for anno in annos:
        if anno["type"] == "variable":
            var_d[anno["name"]] = anno

    # Add equation annotations
    for anno in annos:
        if anno["type"] == "equation":
            matches = anno["matches"]
            for match in matches:
                if match in var_d:
                    var_anno = var_d[match]
                    equations = var_anno.get("equation_annotations", {})
                    equations[anno["latex"]] = []

                    for v in matches[match]:
                        if v == var_anno["id"]:
                            equations[anno["latex"]].append(match)

                    var_anno["equation_annotations"] = equations
                    var_d[match] = var_anno

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
    
    # Add in paper and doi info
    if info != "":
        for item in d:
            contents = d[item]
            contents["file"] = info["pdf_name"]
            contents["doi"] = info["DOI"]
            d[item] = contents

    # Write out
    return json.dumps(d)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pyacset_path", type=str)
    parser.add_argument("-a", "--anno_path", type=str)
    parser.add_argument("-i", "--info_path", type=str)
    parser.add_argument("-o", "--out_dir", type=str)
    args = parser.parse_args()

    out_filename = args.out_dir + "/" + args.anno_path.split("/")[-1].split(".")[0] + "_annotations_dict.json"

    # Get inputs
    jsonFile1 = open(args.pyacset_path, 'r')
    pyacset = json.load(jsonFile1)
    pyacset_s = json.dumps(pyacset)
    jsonFile1.close()

    jsonFile2 = open(args.anno_path, 'r')
    annos = json.load(jsonFile2)
    annos_s = json.dumps(annos)
    jsonFile2.close()

    jsonFile3 = open(args.info_path, 'r')
    info = json.load(jsonFile3)
    info_s = json.dumps(info)
    jsonFile3.close()

    s = link_annos_to_pyacset(pyacset_s, annos_s, info_s)

    with open(out_filename, "w") as f:
        f.write(s)

