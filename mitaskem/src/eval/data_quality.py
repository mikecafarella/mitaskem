import json
import os
import requests

from mitaskem.src.connect import get_gpt4_match
from mitaskem.src.eval.load_concise import extract_text_by_color
from mitaskem.src.mit_extraction import load_arizona_concise_vars

GPT_KEY = os.environ.get('OPENAI_API_KEY')
def extract_content_to_txt(json_input, output_file):
    # Load the JSON data
    with open(json_input, 'r') as file:
        data = json.load(file)


    output_file_name = output_file

    # Open the output file for writing
    with open(output_file_name, 'w') as output_file:
        # Iterate over each item in the JSON data
        for item in data:
            # Extract the content and write it to the output file
            content = item.get('content', '').strip()
            if content:
                output_file.write(content + '\n')

    print(f"Content extracted to {output_file_name}")


def get_mit_variable_eval_prompt(extraction, grdthruth):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/mit_variable_eval_prompt.txt'), "r")
    prompt = text_file.read()
    print(prompt)
    text_file.close()

    prompt = prompt.replace("[EXTRACT]", extraction)
    prompt = prompt.replace("[GROUND]", grdthruth)
    print(prompt)
    return prompt

def evaluate_variable_extraction(extraction, grdthruth, gpt_key):
    prompt = get_mit_variable_eval_prompt(extraction, grdthruth)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4")
    print(ans)
    return ans


def get_var_eval_prompt(extraction, grdthruth):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/var_grd_prompt.txt'), "r")
    prompt = text_file.read()
    # print(prompt)
    text_file.close()

    prompt = prompt.replace("[EXTRACT]", extraction)
    prompt = prompt.replace("[GROUND]", grdthruth)
    # print(prompt)
    return prompt

def evaluate_variable_grd_extraction(extraction, grdthruth, gpt_key):
    prompt = get_var_eval_prompt(extraction, grdthruth)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4-1106-preview")
    # print(ans)
    return ans
def load_concise_vars(input_file_str):
    # Read JSON data from the file
    json_data = json.loads(input_file_str)
    str = ""
    for item in json_data['attributes']:
        if 'id' not in item['payload']:
            continue
        variable_id = item['payload']['id']['id']
        variable_name = item['payload']['mentions'][0]['name']
        value = ""
        for description in item['payload']['text_descriptions']:
            value += '  '
            value += description['description']
        output_line = f"{variable_id}, {variable_name}: {value}\n"
        str += output_line
    return str

def get_mit_model_card_eval_prompt(extraction, grdthruth):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/mit_model_card_eval_prompt.txt'), "r")
    prompt = text_file.read()
    print(prompt)
    text_file.close()

    prompt = prompt.replace("[EXTRACT]", extraction)
    prompt = prompt.replace("[GROUND]", grdthruth)
    print(prompt)
    return prompt

def evaluate_model_card_extraction(extraction, grdthruth, gpt_key):
    prompt = get_mit_model_card_eval_prompt(extraction, grdthruth)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4")
    print(ans)
    return ans


def get_var_whole_prompt(text):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/text_var_val_prompt.txt'), "r")
    prompt = text_file.read()
    # print(prompt)
    text_file.close()

    prompt = prompt.replace("[TEXT]", text)
    # print(prompt)
    return prompt


def get_var_whole_extraction(text, gpt_key):
    prompt = get_var_whole_prompt(text)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4-1106-preview")
    # print(ans)
    return ans


def get_var_cleaning_prompt(text):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/var_cleaning_prompt.txt'), "r")
    prompt = text_file.read()
    # print(prompt)
    text_file.close()

    prompt = prompt.replace("[TEXT]", text)
    # print(prompt)
    return prompt

def get_deduplicate_prompt(text):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/var_dedup_prompt.txt'), "r")
    prompt = text_file.read()
    # print(prompt)
    text_file.close()

    prompt = prompt.replace("[TEXT]", text)
    # print(prompt)
    return prompt


def get_var_cleaning_extraction(text, gpt_key):
    prompt = get_var_cleaning_prompt(text)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4-1106-preview")
    # print(ans)
    return ans

def get_deduplicate_extraction(text, gpt_key):
    prompt = get_deduplicate_prompt(text)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4-1106-preview")
    # print(ans)
    return ans

def get_var_whole_tool_prompt(text, tool):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/text_var_val_tool_prompt.txt'), "r")
    prompt = text_file.read()
    # print(prompt)
    text_file.close()

    prompt = prompt.replace("[TEXT]", text)
    prompt = prompt.replace("[TOOL]", tool)
    # print(prompt)
    return prompt

def get_var_extract_tool_prompt(extract, tool):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/text_var_extract_tool_prompt.txt'), "r")
    prompt = text_file.read()
    # print(prompt)
    text_file.close()

    prompt = prompt.replace("[EXTRACT]", extract)
    prompt = prompt.replace("[TOOL]", tool)
    # print(prompt)
    return prompt


def get_var_whole_tool_extraction(text, tool, gpt_key):
    prompt = get_var_whole_tool_prompt(text, tool)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4-1106-preview")
    # print(ans)
    return ans

def get_var_extract_tool_extraction(extraction, tool, gpt_key):
    prompt = get_var_extract_tool_prompt(extraction, tool)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4-1106-preview")
    # print(ans)
    return ans

def post_pdf_to_api(pdf_file_path):
    url = 'https://api.askem.lum.ai/text-reading/cosmos_to_json'
    headers = {
        'accept': 'application/json',
        # 'Content-Type': 'multipart/form-data' # This header is set automatically by requests when using files parameter
    }
    files = {
        'pdf': (pdf_file_path, open(pdf_file_path, 'rb'), 'application/pdf')
    }
    response = requests.post(url, headers=headers, files=files)

    # Close the file after the request is made
    files['pdf'][1].close()

    if response.status_code == 200:
        return response.json()  # or response.text if the response is not in JSON format
    else:
        print(f"Error: {response.status_code}")
        return None


def count_variable_extraction(text):
    count = 0
    # intialize a set
    var_set = set()
    for line in text.splitlines():
        if line.strip() == "":
            continue
        count += 1
        var_set.add(line)

    # print("count: ", count)
    # print("set: ", len(var_set))
    return len(var_set)

def process_papers():
    # Specify the directory you want to search
    directory = "/Users/chunwei/Downloads/json/"

    # Get a list of all files in the directory with a .json extension
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    # json_files = ["11-16-PAG-annotated-context-annotations-bertozzi-et-al-2020-the-challenges-of-modeling-and-forecasting-the-spread-of-covid-19.json"]

    # Create a csv file to store the results
    csv_file = open('acc_results.csv', 'w')

    # Iterate over each json file
    # add execption handling for each loop

    for json_file in json_files:
        file_name = json_file.replace(".json", "")
        print("Woking on ", file_name)
        try:
            # start to process the file
            paper_name = file_name
            pdf_path = f'/Users/chunwei/Downloads/paper/{paper_name}.pdf'
            result = post_pdf_to_api(pdf_path)

            print(result)
            json_extract = f'/Users/chunwei/Downloads/text/{paper_name}.json'
            # Check if json_response is not None before trying to write to the file
            if result is not None:
                # put the json_response into a file
                with open(json_extract, 'w') as outfile:
                    json.dump(result, outfile)

            # Example usage:
            json_input = json_extract
            paper_text_file = f'/Users/chunwei/Downloads/text/{paper_name}.txt'
            extract_content_to_txt(json_input, paper_text_file)
            # print the content of the txt file
            with open(paper_text_file, 'r') as f:
                text = f.read()
                print(text)
            pure_gpt = get_var_whole_extraction(text, GPT_KEY)
            print(pure_gpt)

            # count how many variables are extracted
            pure_count = count_variable_extraction(pure_gpt)
            print("number of variable in mit extraction: ", pure_count)

            # evaluate the whole text extraction with Arizona tool
            API_ROOT = "https://api.askem.lum.ai/"
            paper_pdf = pdf_path
            with open(paper_pdf, 'rb') as f:
                params = {
                    "annotate_skema": True,
                    "annotate_mit": False
                }
                files = [("pdfs", (paper_pdf, f))]
                response = requests.post(API_ROOT + "text-reading/integrated-pdf-extractions", params=params, files=files)
                json_str = response.text
            print(json_str)

            tool_response_json = json.loads(json_str)
            # create a dummy json file for tool extraction
            tool_json_file = '/tmp/mit-skema.json'
            with open(tool_json_file, 'w') as outfile:
                json.dump(tool_response_json, outfile)
            tool_concise = tool_json_file.replace(".json", "-concise.txt")

            load_arizona_concise_vars(tool_json_file, tool_concise)
            tool_text = open(tool_concise).read()
            print(tool_text)

            count_tool = count_variable_extraction(tool_text)
            print("number of variable in Arizona tool extraction: ", count_tool)

            # test the whole text extraction with Arizona tool
            tool_gpt = get_var_whole_tool_extraction(text, tool_text, GPT_KEY)
            print(tool_gpt)
            count_tool_gpt = count_variable_extraction(tool_gpt)
            print("number of variable in GPT-tool extraction: ", count_tool_gpt)

            # get the ground truth
            ground_truth = f'/Users/chunwei/Downloads/json/{paper_name}.json'
            grd_text = ground_truth.replace(".json", "-concise.txt")
            extract_text_by_color(ground_truth, grd_text, "#ffd100")
            grd_text = open(grd_text).read()
            print(grd_text)

            count_grd = count_variable_extraction(grd_text)
            print("number of variable in ground truth: ", count_grd)

            grd_clean = get_var_cleaning_extraction(grd_text, GPT_KEY)
            print(grd_clean)
            count_grd_clean = count_variable_extraction(grd_clean)
            print("number of variable in cleaned ground truth: ", count_grd_clean)

            # Evaluate the MIT extraction with clean ground truth
            pure_match = evaluate_variable_grd_extraction(pure_gpt, grd_clean, GPT_KEY)
            print(pure_match)
            count_pure_match = count_variable_extraction(pure_match)
            pure_precision = count_pure_match / pure_count
            pure_recall = count_pure_match / count_grd_clean
            print("number of variable in pure match: ", count_pure_match)
            print("precision: ", pure_precision)
            print("recall: ", pure_recall)

            # Evaluate the MIT tool extraction with clean ground truth
            tool_match = evaluate_variable_grd_extraction(tool_gpt, grd_clean, GPT_KEY)
            print(tool_match)
            count_tool_match = count_variable_extraction(tool_match)
            tool_precision = count_tool_match / count_tool_gpt
            tool_recall = count_tool_match / count_grd_clean
            print("number of variable in tool match: ", count_tool_match)
            print("precision: ", tool_precision)
            print("recall: ", tool_recall)

            # Write the results to the csv file: file_name, count_grd, count_grd_clean, pure_count, count_tool_gpt, count_pure_match, count_tool_match, precision_pure, recall_pure, f1_pure, precision_tool, recall_tool, f1_tool
            csv_file.write(f"{file_name},{count_grd},{count_grd_clean},{pure_count},{count_tool_gpt},{count_pure_match},{count_tool_match},{pure_precision},{pure_recall},{2*pure_precision*pure_recall/(pure_precision+pure_recall)},{tool_precision},{tool_recall},{2*tool_precision*tool_recall/(tool_precision+tool_recall)}\n")
        except:
            print("Error: ", file_name)
            continue
    csv_file.close()







if __name__ == "__main__":
    # GPT_KEY = None
    # key = GPT_KEY
    # cache_dir = "/Users/chunwei/research/mitaskem/resources/xDD/"
    #
    # res_mit_file = "mit-extraction/bucky__mit-extraction_id.json"
    #
    # ground_truth = "../../resources/models/Bucky/bucky_variables.txt"
    #
    # mit_concise = res_mit_file.replace(".json", "-concise.txt")
    # # print("file exist: ", os.path.isfile("/tmp/askem/" + res_mit_file))
    # load_concise_vars(
    #     os.path.join(cache_dir, res_mit_file),
    #     os.path.join(cache_dir, mit_concise))
    # mit_text = open(os.path.join(cache_dir, mit_concise)).read()
    #
    # res_arizona_file = "arizona-extraction/bucky_arizona_output_example.json"
    # arizona_concise = res_arizona_file.replace(".json", "-concise.txt")

    # Example usage:

    # API_ROOT = "https://api.askem.lum.ai/"
    # api_endpoint =API_ROOT + "/text-reading/cosmos-to-json"
    # pdf_path = '/Users/chunwei/research/mitaskem/demos/2023-08/sidarthe.pdf'
    # json_response = None  # Initialize json_response to None

    # Usage example:
    # pdf_path = '/Users/chunwei/Downloads/paper/Why is it difficult to accurately predict the COVID-19 epidemic.pdf'
    # # pdf_path = '/Users/chunwei/research/mitaskem/demos/2023-08/sidarthe.pdf'
    # result = post_pdf_to_api(pdf_path)
    # print(result)
    #
    # # Check if json_response is not None before trying to write to the file
    # if result is not None:
    #     # put the json_response into a file
    #     with open('/Users/chunwei/Downloads/sidarthe1218.json', 'w') as outfile:
    #         json.dump(result, outfile)
    #
    process_papers()







