from gpt_interaction import *
from openai import OpenAIError

def get_places(text, gpt_key):
    try:
        prompt = get_petri_places_prompt(text)
        match = get_gpt_match(prompt, gpt_key)
        #print(match)
        places = match.split(":")[-1].split(",")
        return places, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False

def get_parameters(text, gpt_key):
    try:
        prompt = get_petri_parameters_prompt(text)
        match = get_gpt_match(prompt, gpt_key)
        #print(match)
        places = match.split(":")[-1].split(",")
        return places, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False

def get_transitions(text, gpt_key):
    try:
        prompt = get_petri_transitions_prompt(text)
        match = get_gpt_match(prompt, gpt_key, "text-davinci-003")
        #print(match)
        lines = match.split("\n")
        transitions = []
        for line in lines:
            words = [w.rstrip() for w in line.split("->")]
            if (len(words) == 0):
                continue
            transitions.append(words)
        return transitions, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False

def match_place_to_text(text, place, gpt_key):
    try:
        prompt = get_petri_match_place_prompt(text, place)
        match = get_gpt_match(prompt, gpt_key)
        #print(match)
        #places = match.split(":")[-1].split(",")
        return match, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False

if __name__ == "__main__":
    gpt_key = ""
    with open("../resources/models/SEIRD/seird.py", "r") as f:
        code = f.read()
    with open("../resources/models/SEIRD/section2.txt", "r") as f:
        text = f.read()


    places, s = get_places(code, gpt_key)
    parameters, s = get_parameters(code, gpt_key)
    transitions, s = get_transitions(code, gpt_key)

    print(f"places:\t\t{places}")
    print(f"parameters:\t\t{parameters}")
    print(f"transitions:\t\t{transitions}")

    for place in places:
        desc, s = match_place_to_text(text, place, gpt_key)
        print(f"description of {place}: {desc}")