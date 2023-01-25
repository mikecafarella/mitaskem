from gpt_interaction import *
from openai import OpenAIError

def get_places(text, gpt_key):
    try:
        prompt = get_petri_places_prompt(text)
        match = get_gpt_match(prompt, gpt_key)
        places = match.split(":")[-1].split(",")
        return places, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False

def get_transitions(text, gpt_key):
    try:
        prompt = get_petri_transitions_prompt(text)
        match = get_gpt_match(prompt, gpt_key)
        #print(match)
        lines = match.split("\n")
        transitions = []
        for line in lines:
            words = line.split()
            if (len(words) == 0):
                continue
            transitions.append([words[0], words[-1]])
        return transitions, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False



if __name__ == "__main__":
    gpt_key = "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"
    with open("../resources/models/ABC/abc.txt", "r") as f:
        text = f.read()

    places, s = get_places(text, gpt_key)
    transitions, s = get_transitions(text, gpt_key)

    print(f"places:\t\t{places}")
    print(f"transitions:\t\t{transitions}")