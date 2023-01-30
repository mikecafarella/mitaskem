from gpt_interaction import *
from openai import OpenAIError
from connect import *
import re
import argparse

GPT_KEY="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"

def text_param_search(text, gpt_key):
    try:
        prompt = get_text_param_prompt(text)
        match = get_gpt_match(prompt, gpt_key)
        return match, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False

def main(args):

    out_filename = args.out_dir + args.in_path.split("/")[-1].split(".")[0] + "_params.txt"


    with open(args.in_path, "r") as fi, open(out_filename, "w+") as fo:
        text = fi.read()

        text = text[:3000]

        output = text_param_search(text, GPT_KEY)
        print(output)   


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_path", type=str)
    parser.add_argument("-o", "--out_dir", type=str, default="resources/jan_evaluation/cosmos_params")
    args = parser.parse_args()

    main(args)