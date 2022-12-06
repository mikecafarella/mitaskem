import re
from cryptography.fernet import Fernet
import openai
from openai import OpenAIError


def index_text(text_path: str) -> str:
    fw = open(text_path+"_idx", "w")
    with open(text_path) as fp:
        for i, line in enumerate(fp):
            fw.write('%d\t%s' % (i, line))
    fw.close()
    return text_path+"_idx"


def get_gpt_match(prompt):
    mykey = b'Z1QFxceGL_s6karbgfNFyuOdQ__m5TfHR7kuLPJChgs='
    enc = b'gAAAAABjRh0iNbsVb6_DKSHPmlg3jc4svMDEmKuYd-DcoTxEbESYI9F8tm8anjbsTsZYHz_avZudJDBdOXSHYZqKmhdoBcJd919hCffSMg6WFYP12hpvI7EeNppGFNoZsLGnDM5d6AOUeRVeIc2FbmB_j0vvcIwuEQ=='
    fernet = Fernet(mykey)
    # openai.api_key = fernet.decrypt(enc).decode()
    openai.api_key = "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"
    # prompt = "Please write me a sentence\n\n"
    response = openai.Completion.create(model="text-davinci-002", prompt=prompt, temperature=0.0, max_tokens=256)
    result = response.choices[0].text.strip()
    # print(result)
    return result
def read_text_from_file(text_path):
    text_file = open(text_path, "r")
    prompt = text_file.read()
    return prompt

# Get gpt-3 prompt with variables, ontology terms and match targets
def get_prompt(vars, terms, target):
    text_file = open("model/prompt.txt", "r")
    prompt = text_file.read()
    text_file.close()

    vstr = ''
    vlen = len(vars)
    i = 1;
    for v in vars:
        vstr += str(i) + " (" + str(v[1])+", "+str(v[2])+")\n"
        i+=1;
    # print(vstr)
    tstr = '['+', '.join(terms)+']'
    tlen = len(terms)
    # print(tstr)
    prompt = prompt.replace("[VAR]", vstr)
    prompt = prompt.replace("[VLEN]", str(vlen))
    prompt = prompt.replace("[TERMS]", tstr)
    prompt = prompt.replace("[TLEN]", str(tlen))
    prompt = prompt.replace("[TARGET]", target)
    # print(prompt)
    return prompt



# Get gpt-3 prompt with formula, code terms and match formula targets
def get_formula_code_prompt(code, formula, target):
    text_file = open("model/formula_code_prompt.txt", "r")
    prompt = text_file.read()
    text_file.close()

    prompt = prompt.replace("[CODE]", code)
    prompt = prompt.replace("[FORMULA]", formula)
    prompt = prompt.replace("[TARGET]", target)
    # print(prompt)
    return prompt

# Get gpt-3 prompt with formula, code terms and match formula targets
def get_code_text_prompt(code, text, target):
    text_file = open("model/code_text_prompt.txt", "r")
    prompt = text_file.read()
    text_file.close()

    prompt = prompt.replace("[CODE]", code)
    prompt = prompt.replace("[TEXT]", text)
    prompt = prompt.replace("[TARGET]", target)
    # print(prompt)
    return prompt


def get_variables(path):
    list = []
    with open(path) as myFile:
        for num, line in enumerate(myFile, 1):
            match = re.match(r'\s*(\S+)\s*=\s*([-+]?(?:\d*\.\d+|\d+))\s*', line)
            if match:
                para = match.group(1)
                val = match.group(2)
                # print(num, ",", para, ",", val)
                list.append((num, para, val))
    print((list))
    return list

def get_match(vars, terms, target):
    prompt = get_prompt(vars, terms, target)
    match = get_gpt_match(prompt)
    val = match.split("(")[1].split(",")[0]
    return val

def match_code_targets(targets, code_path, terms):
    vars = get_variables(code_path)
    vdict = {}
    connection = []
    for idx, v in enumerate(vars):
        vdict[v[1]] = idx
    for t in targets:
        val = get_match(vars, terms, t)
        connection.append((t,{val: "grometSubObject"}, float(vars[vdict[val]][2]),  vars[vdict[val]][0]))
    return connection


def match_gromet_targets(targets, vars, vdict, terms):
    vlist = []
    for v in vars:
#         print( type(vdict[v][2]))
        vlist.append((vdict[v][2].to_dict()['line_begin'], v, vdict[v][1].to_dict()['value']))
    connection = []
    for t in targets:
        val = get_match(vlist, terms, t)
        # print(val)
        connection.append((t,{val: "grometSubObject"}, float(vdict[val][1].to_dict()['value']),  vdict[val][2].to_dict()['line_begin']))
    return connection


def ontology_code_connection():
    terms = ['population', 'doubling time', 'recovery time', 'infectious time']
    code = "model/SIR/CHIME_SIR_while_loop.py"
    targets = ['population', 'infectious time']
    val = []
    try:
        val = match_code_targets(targets, code, terms)
    except OpenAIError as err:
        print("OpenAI connection error:", err)
        print("Using hard-coded connections")
        val = [("infectious time", {"name": "grometSubObject"}, 14.0, 67),("population", {"name": "grometSubObject"}, 1000, 80)]
    print(val)

def code_text_connection():
    code = "model/SIR/CHIME_SIR_while_loop.py"
    code_str = read_text_from_file(code)
    text = "model/SIR/description.txt"
    idx_text = read_text_from_file(index_text(text))
    targets = ['get_growth_rate', 'get_beta']
    try:
        for t in targets:
            prompt = get_code_text_prompt(code_str, idx_text, t)
            match = get_gpt_match(prompt)
            # val = match.split("(")[1].split(",")[0]
            print("Best description for python function {} is in lines {}".format(t, match))
    except OpenAIError as err:
        print("OpenAI connection error:", err)


def formula_code_connection():
    code = "model/SVIIvR/CHIME_SVIIvR.py"
    code_str = read_text_from_file(code)
    formula = "model/SVIIvR/formula.tex_idx"
    formula_text = read_text_from_file(formula)
    targets = ['1', '2', '3', '4', '5']
    try:
        for t in targets:
            prompt = get_formula_code_prompt(code_str, formula_text, t)
            match = get_gpt_match(prompt)
            # val = match.split("(")[1].split(",")[0]
            print("{}\n\n".format( match))
    except OpenAIError as err:
        print("OpenAI connection error:", err)

# print("======================Formula to code matching=====================")
# formula_code_connection()
# print("======================Code to text matching=====================")
# code_text_connection()
# ontology_code_connection()
# print(get_gpt_match(read_text_from_file("model/code_paper_prompt.txt")))
# get_variables("/Users/chunwei/research/ASKEM-data/epidemiology/Bucky/code/bucky_simplified_v1.py")