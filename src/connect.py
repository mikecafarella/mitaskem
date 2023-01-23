import os
import re
import pandas as pd
from cryptography.fernet import Fernet
import openai
from openai import OpenAIError

GKEY = "GIVEN_GPT_KEY"

def index_text_path(text_path: str) -> str:
    fw = open(text_path + "_idx", "w")
    with open(text_path) as fp:
        for i, line in enumerate(fp):
            fw.write('%d\t%s' % (i, line))
    fw.close()
    return text_path + "_idx"

def index_text(text: str) -> str:
    idx_text = ""
    tlist = text.split('\n')
    # print(tlist)
    for i, line in enumerate(tlist):
        if i==len(tlist)-1 and line== "":
            break
        idx_text = idx_text + ('%d\t%s\n' % (i, line))
    return idx_text




def get_gpt_match(prompt):
    # mykey = b'Z1QFxceGL_s6karbgfNFyuOdQ__m5TfHR7kuLPJChgs='
    # enc = b'gAAAAABjRh0iNbsVb6_DKSHPmlg3jc4svMDEmKuYd-DcoTxEbESYI9F8tm8anjbsTsZYHz_avZudJDBdOXSHYZqKmhdoBcJd919hCffSMg6WFYP12hpvI7EeNppGFNoZsLGnDM5d6AOUeRVeIc2FbmB_j0vvcIwuEQ=='
    # fernet = Fernet(mykey)
    # openai.api_key = fernet.decrypt(enc).decode()
    openai.api_key = GKEY
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
        vstr += str(i) + " (" + str(v[1]) + ", " + str(v[2]) + ")\n"
        i += 1;
    # print(vstr)
    tstr = '[' + ', '.join(terms) + ']'
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
    text_file = open(os.path.join(os.path.dirname(__file__), 'model/code_text_prompt.txt'), "r")
    prompt = text_file.read()
    text_file.close()

    prompt = prompt.replace("[CODE]", code)
    prompt = prompt.replace("[TEXT]", text)
    prompt = prompt.replace("[TARGET]", target)
    # print(prompt)
    return prompt


# Get gpt-3 prompt with code, dataset and match function targets
def get_code_dataset_prompt(code, dataset, target):
    text_file = open("model/code_dataset_prompt.txt", "r")
    prompt = text_file.read()
    text_file.close()

    prompt = prompt.replace("[CODE]", code)
    prompt = prompt.replace("[DATASET]", dataset)
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
    print("Extracted variables: ", list)
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
        connection.append((t, {val: "grometSubObject"}, float(vars[vdict[val]][2]), vars[vdict[val]][0]))
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
        connection.append((t, {val: "grometSubObject"}, float(vdict[val][1].to_dict()['value']),
                           vdict[val][2].to_dict()['line_begin']))
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
        val = [("infectious time", {"name": "grometSubObject"}, 14.0, 67),
               ("population", {"name": "grometSubObject"}, 1000, 80)]
    print(val)

def extract_ints(str):
    return re.findall(r'\d+', str)

def code_text_connection(code, text, interactive = False):
    code_str = code
    idx_text = index_text(text)
    tlist = text.split("\n")
    targets = ['get_growth_rate', 'get_beta']
    try:
        for t in targets:
            prompt = get_code_text_prompt(code_str, idx_text, t)
            match = get_gpt_match(prompt)
            ilist = extract_ints(match)
            # val = match.split("(")[1].split(",")[0]
            if interactive: 
                print("Best description for python function {} is in lines {}-{}:".format(t, ilist[0], ilist[-1]))
                select_text(tlist, int(ilist[0]), int(ilist[-1]), 1)
                print("---------------------------------------")
            else:
                return tlist, int(ilist[0]), int(ilist[-1])
    except OpenAIError as err:
        print("OpenAI connection error:", err)
        return ""


def code_dataset_connection(code, dataset, interactive=False):
    code_str = code
    parse_dataset(dataset)
    d_text = read_text_from_file(os.path.join(dataset, "headers.txt"))
    targets = ['estimate_chr', 'estimate_cfr']
    try:
        for t in targets:
            prompt = get_code_dataset_prompt(code_str, d_text, t)
            match = get_gpt_match(prompt)
            returnable = ""
            if len(match.split("dataset.")) == 1:
                returnable = match
            else:
                returnable = match.split("dataset.")[0]+"dataset."

            if interactive:
                print(returnable)
                print("---------------------------------------")
            else:
                return returnable
            # ilist = extract_ints(match)
            # val = match.split("(")[1].split(",")[0]
            # print("Best description for python function {} is in lines {}-{}:".format(t, ilist[0], ilist[-1]))
            # select_text(read_lines(text), int(ilist[0]), int(ilist[-1]), 1)
    except OpenAIError as err:
        print("OpenAI connection error:", err)
        return ""


def read_lines(filename):
    lines = []
    with open(filename) as file:
        for line in file:
            # print(line)
            lines.append(line.rstrip())
    return lines


def select_text(lines, s, t, buffer):
    start = s - buffer
    end = t + buffer
    if start < 0:
        start = 0
    if end >= len(lines):
        end = len(lines) - 1
    for i in range(start, end+1):
        if i<=t and i>=s:
            print(">>\t{}\t{}".format(i,lines[i]))
        else:
            print("\t{}\t{}".format(i, lines[i]))

def formula_code_connection(code, formula, interactive = False):
    code_str = code
    formula_text = formula
    flist = formula.split("\n")
    if flist[-1]=="":
        del flist[-1]
    targets = ['1', '2', '3', '4', '5']
    try:
        for t in flist:
            prompt = get_formula_code_prompt(code_str, formula_text, t)
            match = get_gpt_match(prompt)
            # val = match.split("(")[1].split(",")[0]
            if interactive:
                print("{}\n---------------------------------------\n".format(match))
            else:
                return match
    except OpenAIError as err:
        print("OpenAI connection error:", err)
        return ""


def parse_dataset(dir):
    mml = os.path.join(dir, 'headers.txt')
    fw = open(mml, "w")
    for filename in os.listdir(dir):
        data_path = os.path.join(dir, filename)
        # checking if it is a png file
        if os.path.isfile(data_path) and data_path.endswith(".csv"):
            fw.write("{}:\t{}\n".format(filename, read_text_from_file(data_path).split('\n')[0]))
    fw.close()


def print_list(dir):
    print("ls ", dir)
    for filename in os.listdir(dir):
        if filename.endswith(".csv"):
            print("\t",filename)


DATASET_INFO = {
    "nychealth.csv": "NYC Health Covid data with 1011 rows x 67 columns",
    "covid_confirmed_usafacts.csv": "USA Covid confirmed cases with 3194 rows x 557 columns (truncated columns)",
    "covid_deaths_usafacts.csv": "USA Covid death cases with 3194 rows x 557 columns (truncated columns)",
    "covid_tracking.csv": "Covid tracking data with 20781 rows x 56 columns",
    "usafacts_hist.csv": "Fact Covid data (adm2) with 1800367 rows x 5 columns"
}
def print_df(dir):
    print("We have a set of datasets:")
    print("---------------------------------------")
    for filename in os.listdir(dir):
        if filename.endswith(".csv"):
            print(DATASET_INFO[filename]+". Schema and data sample:")
            df = pd.read_csv (os.path.join(dir, filename))
            print(df)
            print("---------------------------------------")


def get_df(dir):
    dfs = []
    for filename in os.listdir(dir):
        if filename.endswith(".csv"):
            df = pd.read_csv (os.path.join(dir, filename))
            dfs.append((DATASET_INFO[filename], df))
    return dfs
# parse_dataset("./model/Bucky/data_sample/")
# dfs = get_df("./model/Bucky/data_sample/")
# print(dfs[0][0])
# print(dfs[0][1])
# code_dataset_connection("./model/Bucky/bucky_sample.py", "./model/Bucky/data_sample/")
# print("======================Formula to code matching=====================")
# formula_code_connection()
# print("======================Code to text matching=====================")
# code_text_connection()
# ontology_code_connection()
# print(get_gpt_match(read_text_from_file("model/code_paper_prompt.txt")))
# get_variables("/Users/chunwei/research/ASKEM-data/epidemiology/Bucky/code/bucky_simplified_v1.py")
# lines = read_lines("./model/SIR/description.txt")
# select_text(lines, 7, 27, 5)
# code = "model/SIR/CHIME_SIR_while_loop.py"
# text = "model/SIR/description.txt"
# code_text_connection(code,text)
# print(index_text("line1\nline2\nline3"))
# print("this is a dataset. while this is antoher.".split("dataset. ")[0] + "dataset.")