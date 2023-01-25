import os
import re
import pandas as pd
from cryptography.fernet import Fernet
import openai
from openai import OpenAIError
from util import *
from gpt_interaction import *
from mira_dkg_interface import *
from automates.program_analysis.JSON2GroMEt.json2gromet import json_to_gromet
from automates.gromet.query import query

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



def code_text_connection(code, text, gpt_key, interactive = False):
    code_str = code
    idx_text = index_text(text)
    tlist = text.split("\n")
    targets = extract_func_names(code_str)
    print(f"TARGETS: {targets}")
    tups = []
    try:
        for t in targets:
            prompt = get_code_text_prompt(code_str, idx_text, t)
            match = get_gpt_match(prompt, gpt_key)
            ilist = extract_ints(match)
            ret_s = select_text(tlist, int(ilist[0]), int(ilist[-1]), 1, interactive)
            if interactive: 
                print("Best description for python function {} is in lines {}-{}:".format(t, ilist[0], ilist[-1]))
                print(ret_s)
                print("---------------------------------------")
            else:
                tups.append((t, int(ilist[0]), int(ilist[-1]), ret_s))
        return tups, True
    except OpenAIError as err:
        if interactive:
            print("OpenAI connection error:", err)
        else:
            return f"OpenAI connection error: {err}", False


def code_dataset_connection(code, schema, gpt_key, interactive=False):
    targets = extract_func_names(code)
    tups = []
    try:
        for t in targets:
            prompt = get_code_dataset_prompt(code, schema, t)
            match = get_gpt_match(prompt, gpt_key)
            returnable = match.split("function are the ")[1].split(" columns.")[0].split(" and ")

            if interactive:
                print(returnable)
                print("---------------------------------------")
            else:
                tups.append((t, returnable))
        return tups, True
    except OpenAIError as err:
        if interactive:
            print("OpenAI connection error:", err)
        else:
            return f"OpenAI connection error: {err}",False


def select_text(lines, s, t, buffer, interactive=True):
    ret_s = ""
    start = s - buffer
    end = t + buffer
    if start < 0:
        start = 0
    if end >= len(lines):
        end = len(lines) - 1
    for i in range(start, end+1):
        if i<=t and i>=s:
            if interactive:
                ret_s += ">>\t{}\t{}".format(i,lines[i])
            else:
                ret_s += lines[i]
        elif interactive:
            ret_s += "\t{}\t{}".format(i, lines[i])
    return ret_s

def code_formula_connection(code, formulas, gpt_key):
    flist = formulas.split("\n")
    matches = []
    if flist[-1]=="":
        del flist[-1]
    try:
        for t in flist:
            prompt = get_code_formula_prompt(code, formulas, t)
            match = get_gpt_match(prompt, gpt_key)
            
            matches.append([t, match.split(":")[1]])
        return matches, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False

DEFAULT_TERMS = ['population', 'doubling time', 'recovery time', 'infectious time']
DEFAULT_ATTRIBS = ['description', 'synonyms', 'xrefs', 'suggested_unit', 'suggested_data_type',
           'physical_min', 'physical_max', 'typical_min', 'typical_max']

def code_dkg_connection(dkg_targets, gpt_key, ontology_terms=DEFAULT_TERMS, ontology_attribs=DEFAULT_ATTRIBS):

    gromet_fn_module = json_to_gromet("gromet/CHIME_SIR_while_loop--Gromet-FN-auto.json")
    nops = query.collect_named_output_ports(gromet_fn_module)

    terms = list(build_local_ontology(ontology_terms, ontology_attribs).keys())
    variables = set()
    var_dict = {}
    for nop in nops:
        if nop[1] is not None:
            variables.add(nop[0])
            var_dict[nop[0]] = nop

    vlist = []
    for v in list(variables):
        vlist.append((var_dict[v][2].to_dict()['line_begin'], v, var_dict[v][1].to_dict()['value']))
    connection = []
    for t in dkg_targets:
        prompt = get_code_dkg_prompt(vlist, terms, t)
        match = get_gpt_match(prompt, gpt_key)
        val = match.split("(")[1].split(",")[0]

        connection.append((t, {val: "grometSubObject"}, float(var_dict[val][1].to_dict()['value']),
                           var_dict[val][2].to_dict()['line_begin']))

    print(connection)
    return connection

if __name__ == "__main__":
    code_dkg_connection("population", "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")
