from gpt_interaction import get_petri_places_prompt, get_gpt_match
from openai import OpenAIError

def get_places(text, gpt_key):
    try:
        prompt = get_petri_places_prompt(text)
        match = get_gpt_match(prompt, gpt_key)
        places = match.split(":")[-1].split(",")
        return places, True
    except OpenAIError as err:   
        return f"OpenAI connection error: {err}", False

if __name__ == "__main__":
    with open("../resources/models/ABC/abc.txt", "r") as f:
        text = f.read()

    places, s = get_places(text, "")

    

    print(places)