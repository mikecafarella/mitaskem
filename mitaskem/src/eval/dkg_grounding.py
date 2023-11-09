import json
import pandas as pd

def extract_info(json_obj):
    result = []
    for attribute in json_obj['attributes']:
        if attribute['type'] != 'anchored_entity':
            continue
        info = {}
        if 'id' in attribute['payload']:
            info['variable_id'] = attribute['payload']['id']['id']
        if attribute['payload']['mentions']:
            info['variable_name'] = attribute['payload']['mentions'][0]['name']
        if attribute['payload']['text_descriptions']:
            info['variable_description'] = attribute['payload']['text_descriptions'][0]['description']
        if 'groundings' in attribute['payload']:
            info['grounding'] = [{'id': g['grounding_id'], 'value': g['grounding_text']} for g in attribute['payload']['groundings']]
        result.append(info)
    return result

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)


def main():
    with open('/Users/chunwei/Downloads/mit-response_5.json', 'r') as f:
        json_obj = json.load(f)
    info = extract_info(json_obj)
    save_to_excel(info, 'output5.xlsx')

if __name__ == "__main__":
    main()