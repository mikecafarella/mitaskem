
import argparse
import json
import unicodedata as ud
import ast

greek_alphabet = {
    u'\u0391': 'Alpha',
    u'\u0392': 'Beta',
    u'\u0393': 'Gamma',
    u'\u0394': 'Delta',
    u'\u0395': 'Epsilon',
    u'\u0396': 'Zeta',
    u'\u0397': 'Eta',
    u'\u0398': 'Theta',
    u'\u0399': 'Iota',
    u'\u039A': 'Kappa',
    u'\u039B': 'Lamda',
    u'\u039C': 'Mu',
    u'\u039D': 'Nu',
    u'\u039E': 'Xi',
    u'\u039F': 'Omicron',
    u'\u03A0': 'Pi',
    u'\u03A1': 'Rho',
    u'\u03A3': 'Sigma',
    u'\u03A4': 'Tau',
    u'\u03A5': 'Upsilon',
    u'\u03A6': 'Phi',
    u'\u03A7': 'Chi',
    u'\u03A8': 'Psi',
    u'\u03A9': 'Omega',
    u'\u03B1': 'alpha',
    u'\u03B2': 'beta',
    u'\u03B3': 'gamma',
    u'\u03B4': 'delta',
    u'\u03B5': 'epsilon',
    u'\u03B6': 'zeta',
    u'\u03B7': 'eta',
    u'\u03B8': 'theta',
    u'\u03B9': 'iota',
    u'\u03BA': 'kappa',
    u'\u03BB': 'lamda',
    u'\u03BC': 'mu',
    u'\u03BD': 'nu',
    u'\u03BE': 'xi',
    u'\u03BF': 'omicron',
    u'\u03C0': 'pi',
    u'\u03C1': 'rho',
    u'\u03C3': 'sigma',
    u'\u03C4': 'tau',
    u'\u03C5': 'upsilon',
    u'\u03C6': 'phi',
    u'\u03C7': 'chi',
    u'\u03C8': 'psi',
    u'\u03C9': 'omega',
}


def link_annos_to_pyacset(pyacset_s, annos_s, info_s=""):
    pyacset = ast.literal_eval(pyacset_s)
    annos = ast.literal_eval(annos_s)
    greek_set = {greek_alphabet[sub].upper() for sub in greek_alphabet}
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
        if name.upper() in greek_set:
            d[uid] = var_d.get(ud.lookup(f"GREEK SMALL LETTER {name.upper()}"), {})
        else:
            d[uid] = var_d.get(name, {})
    
    # Add in paper and doi info
    if info_s != "":
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

