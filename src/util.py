import re
import os

def extract_ints(str):
    return re.findall(r'\d+', str)

def extract_func_names(code):
    tups = re.findall(r'(def)\s(\w+)\([a-zA-Z0-9_:\[\]=,\s]*\):', code)
    return [x[1] for x in tups]

def read_text_from_file(text_path):
    text_file = open(text_path, "r")
    prompt = text_file.read()
    return prompt

def extract_headers(dir):
    fw = open(os.path.join(os.path.dirname(__file__), dir, 'headers.txt'), "w+")
    for filename in os.listdir(dir):
        data_path = os.path.join(dir, filename)
        # checking if it is a png file
        if os.path.isfile(data_path) and data_path.endswith(".csv"):
            fw.write("{}:\t{}\n".format(filename, read_text_from_file(data_path).split('\n')[0]))
    fw.close()

def pretty_print(l):
    for i in l:
        print(f"{i}\n-------------------------------------\n")