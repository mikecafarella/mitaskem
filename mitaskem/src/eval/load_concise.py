import json
import os

from mitaskem.src.mit_extraction import load_concise_vars


def extract_text_by_color(input_file, output_file, color="#ffd100"):
    # Read JSON data from the file
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Extract relevant information
    output = []
    for item in data:
        # Check if the color matches
        if item.get('color') == color:
            # Extract the text
            text = item.get('text')
            # Append the text to the output list
            output.append(text + "\n")

    # Open a new file to write the output
    with open(output_file, 'w') as output_file:
        # Write the extracted information to the output file
        output_file.writelines(output)

if __name__ == "__main__":
    GPT_KEY = None
    key = GPT_KEY
    cache_dir = "/Users/chunwei/Downloads/"

    res_file = "sidarthe_annotations-mit.json"

    ground_truth = ""

    res_concise = res_file.replace(".json", "-concise.txt")

    # extract_text_by_color(
    #     os.path.join(cache_dir, res_file),
    #     os.path.join(cache_dir, res_concise),"#f9cd59")
    # print("file exist: ", os.path.isfile("/tmp/askem/" + res_mit_file))
    load_concise_vars(
        os.path.join(cache_dir, res_file),
        os.path.join(cache_dir, res_concise))

    # load_arizona_concise_vars(
    #     os.path.join(cache_dir, res_file),
    #     os.path.join(cache_dir, res_concise))