import argparse

def main(args):

    out_filename = args.out_dir + "/" + args.in_path.split("/")[-1].split(".")[0] + "_deduped.txt"

    var_dict = {}

    # Build dictionary, deduplicating along the way
    with open(args.in_path, "r") as f:
        for line in f:
            toks = line.rstrip().split(":")

            if len(toks) == 1:
                continue

            var_name = toks[0]
            var_desc = toks[1]

            desc_list = var_dict.get(var_name, [])
            desc_list.append(var_desc)

            var_dict[var_name] = desc_list

    # Write dictionary out
    with open(out_filename, "w+") as f:
        for var_name in var_dict:
            f.write(f"{var_name}: ")

            for desc in var_dict[var_name]:
                f.write(f"{desc}; ")
            
            f.write("\n")

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_path", type=str)
    parser.add_argument("-o", "--out_dir", type=str, default="resources/jan_evaluation/cosmos_params")
    args = parser.parse_args()

    main(args)