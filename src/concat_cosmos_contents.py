import json
import argparse

def main(args):
    jsonFile = open(args.in_path, 'r')
    values = json.load(jsonFile)
    jsonFile.close()

    filename = args.in_path.split("/")[-1].split("_")[1].split("--")[0] + ".txt"

    with open(args.out_dir + "/" + filename, "w+") as f:
        for item in values:
            f.write(item['content'] + "\n")

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_path", type=str)
    parser.add_argument("-o", "--out_dir", type=str, default="resources/jan_evaluation/cosmos_txt")
    args = parser.parse_args()

    main(args)