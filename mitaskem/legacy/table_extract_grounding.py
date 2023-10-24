from mitaskem.src.mira_dkg_interface import *
import re

def ground(csv_path:str) -> str:
    with open(csv_path, "r") as f:
        lines = f.readlines()

        for line in lines:
            print(f"-----------\n\n{line}")
            toks = line.rstrip().split(",")
            if len(toks) == 0:
                continue

            for tok in toks: 
                if str.isdigit(toks[0]) or re.search("table", tok, re.IGNORECASE):
                    continue
                if re.search("^[A-Za-z]{2,}\s[A-Za-z]{2,}$|^[A-Za-z]{2,}$", tok):
                    print(f"looking up {tok}")
                    print(get_mira_dkg_term(tok, ['id', 'name']))

    return ""







if __name__=="__main__":
    print(ground("../resources/xdd_extracts/tables/5e86d13d998e17af826a2572_1.csv"))