
import argparse
import json
import unicodedata as ud


def main(args):

    out_filename = args.out_dir + "/" + "metadata_real.json"

    # Get states
    jsonFile = open(args.in_path, 'r')
    values = json.load(jsonFile)
    jsonFile.close()

    # Get dict of annotations
    f = open(args.anno_path, "r")
    anno_dict = {}
    for line in f:
        toks = line.split(":")
        anno_dict[toks[0]] = toks[1].rstrip()
    f.close

    # Produce output
    f = open(out_filename, "w+")
    f.write("{")
    flag = False

    states = values["S"]
    for state in states:
        name = state["sname"].lstrip().rstrip()
        uid = state["uid"]

        if flag:
            f.write(",")
        else: 
            flag = True

        metadata = anno_dict[name]

        f.write(f"\"{uid}\": \"{metadata}\"")

    transitions = values["T"]
    for tr in transitions:
        name = tr["tname"].lstrip().rstrip()
        uid = tr["uid"]

        f.write(",")
        
        metadata = anno_dict[ud.lookup(f"GREEK SMALL LETTER {name.upper()}")]

        f.write(f"\"{uid}\": \"{metadata}\"")




    f.write("}")




if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_path", type=str)
    parser.add_argument("-a", "--anno_path", type=str)
    parser.add_argument("-o", "--out_dir", type=str, default="resources/jan_evaluation/cosmos_params")
    args = parser.parse_args()

    main(args)