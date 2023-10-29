from mitaskem.src.connect import dataset_header_dkg
import os
import csv
import os
import csv
import json


def process_csv_files(input_file, output_json_file):
    annotations = []

    # Read file paths from input_file (output.csv)
    with open(input_file, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row

        for row in reader:
            file_path = row[0]
            print("Parsing file: {}", file_path)
            # Read header from the .csv file
            with open(file_path, 'r') as csv_file:
                header = csv_file.readline()
                print("Parsing header: {}", header)
                if "http:" in header:
                    continue
                if "https:" in header:
                    continue
                if "2020-" in header:
                    annotations.append({
                        'file_name': os.path.basename(file_path),
                        'file_directory': os.path.dirname(file_path),
                        'annotation': "too many date columns",
                        'source': "MIT data profiling tool http://100.26.10.46"
                    })
                    continue
                if "2021-" in header:
                    annotations.append({
                        'file_name': os.path.basename(file_path),
                        'file_directory': os.path.dirname(file_path),
                        'annotation': "too many date columns",
                        'source': "MIT data profiling tool http://100.26.10.46"
                    })
                    continue
                if "2022-" in header:
                    annotations.append({
                        'file_name': os.path.basename(file_path),
                        'file_directory': os.path.dirname(file_path),
                        'annotation': "too many date columns",
                        'source': "MIT data profiling tool http://100.26.10.46"
                    })
                    continue
                print("Processing header: {}", header)
                json_annotation, res = dataset_header_dkg(header, GPT_KEY)

                annotations.append({
                    'file_name': os.path.basename(file_path),
                    'file_directory': os.path.dirname(file_path),
                    'annotation': json.loads(json_annotation),
                    'source': "MIT data profiling tool http://100.26.10.46"
                })

    # Write annotations to the output JSON file
    with open(output_json_file, 'w') as f:
        json.dump(annotations, f, indent=2)


def collect_csv_files(start_directory, output_file):
    csv_files = []

    # Recursively collect all .csv files and their paths
    for root, _, files in os.walk(start_directory):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))

    # Write the collected paths to a new .csv file
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['File Path'])  # Header row
        for file_path in csv_files:
            writer.writerow([file_path])




if __name__ == "__main__":
    # code_dkg_connection("population", "") # GPT key
    # vars = read_text_from_file('../demos/2023-03-19/mar_demo_intermediate.json')
    # dataset = read_text_from_file('../resources/dataset/headers.txt')
    # match, _ = vars_dataset_connection(vars, dataset, GPT_KEY)
    # print(match)

    # res, yes = dataset_header_dkg("demographic_category,demographic_value,total_cases",GPT_KEY)
    # print(res)

    # Usage:
    start_directory = '/Users/chunwei/research/data-truth'
    output_file = 'csv_list_output.csv'
    collect_csv_files(start_directory, output_file)

    # # Usage:
    input_file = output_file
    output_json_file = 'ensemble/data-truth_annotations.json'
    process_csv_files(input_file, output_json_file)