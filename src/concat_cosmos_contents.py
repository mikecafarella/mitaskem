import json
import argparse
import re 

def main(args):
    jsonFile = open(args.in_path, 'r')
    values = json.load(jsonFile)
    jsonFile.close()

    filename = args.in_path.split("/")[-1].split("_")[1].split("--")[0] + ".txt"
    doi = []
    doi_regex = re.compile('https://doi\.org\S+\s+[0-9-]+')

    with open(args.out_dir + "/" + filename, "w+") as f:
        for item in values:
            f.write(item['content'] + "\n")
            matches = doi_regex.findall(item['content'])
            if len(matches) > 0:
                doi.append(matches[0].replace(" ", ""))


    filename_2 = args.in_path.split("/")[-1].split("_")[1].split("--")[0] + "_info.json"
    d = {}
    d["pdf_name"] = values[0]["pdf_name"]
    d["DOI"] = doi[0]
    with open(args.out_dir + "/" + filename_2, "w+") as f:
        json.dump(d,f)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_path", type=str)
    parser.add_argument("-o", "--out_dir", type=str, default="resources/jan_evaluation/cosmos_txt")
    args = parser.parse_args()

    main(args)