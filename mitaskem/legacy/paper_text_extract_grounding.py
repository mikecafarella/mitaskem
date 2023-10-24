from mira_dkg_interface import *
import re

def ground(text_path:str) -> str:
    """
    Grounding the paper text to DKG terms
    :param text_path: File path of the arizona-extraction file from extract from paper
    :return: Matches from DKG
    """
    with open(text_path, "r") as f:
        lines = f.readlines()

        for line in lines:
            print(f"-----------\n\n{line}")
            toks = line.rstrip().split(": ")
            if len(toks) < 2:
                continue

            for tok in toks: 
                if str.isdigit(toks[0]):
                    continue
                if re.search("^[A-Za-z]{2,}\s[A-Za-z]{2,}$|^[A-Za-z]{2,}$", tok):
                    print(f"looking up {tok}")
                    print(get_mira_dkg_term(tok, ['id', 'name']))

    return ""

if __name__=="__main__":
    print(ground("../resources/jan_evaluation/scenario_2_sidarthe/sidarthe_vars.txt"))