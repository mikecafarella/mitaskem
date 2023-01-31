from gpt_interaction import *
from openai import OpenAIError
from connect import *
import re
import argparse
from gpt_key import *


def text_param_search(text, gpt_key):
    try:
        prompt = get_text_param_prompt(text)
        match = get_gpt_match(prompt, gpt_key, "text-davinci-003")
        return match, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False

def text_var_search(text, gpt_key):
    try:
        prompt = get_text_var_prompt(text)
        match = get_gpt_match(prompt, gpt_key, "text-davinci-003")
        return match, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False


def main(args):

    out_filename_params = args.out_dir + "/" + args.in_path.split("/")[-1].split(".")[0] + "_params.txt"
    out_filename_vars = args.out_dir + "/" + args.in_path.split("/")[-1].split(".")[0] + "_vars.txt"

    with open(args.in_path, "r") as fi, open(out_filename_params, "w+") as fop, open(out_filename_vars, "w+") as fov:
        text = fi.read()
        length = len(text)
        segments = int(length/3500 + 1)

        for i in range(segments):
            snippet = text[i * 3500: (i+1) * 3500]

            output, success = text_param_search(snippet, GPT_KEY)
            if success:
                print("OUTPUT (params): " + output + "\n------\n")  
                if output != "None":
                    fop.write(output + "\n") 

            output, success = text_var_search(snippet, GPT_KEY)
            if success:
                print("OUTPUT (vars): " + output + "\n------\n")  
                if output != "None":
                    fov.write(output + "\n") 

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_path", type=str)
    parser.add_argument("-o", "--out_dir", type=str, default="resources/jan_evaluation/cosmos_params")
    args = parser.parse_args()

    main(args)