import json


def find_column_info(dataset_name, column_name, datafile):
    dataset_id = -1
    column_id = -1
    found = False

    # Load dataset file
    with open(datafile, "r") as mapping_file:
        data = mapping_file.readlines()

    for i, row in enumerate(data):
        file_name, columns = row.strip('\n').split(':')
        columns_list = columns.strip(' ').split(',')

        if file_name.strip() == dataset_name:
            dataset_id = i
            if column_name in columns_list:
                column_id = columns_list.index(column_name)
                found = True
                break

    if found:
        return dataset_id, dataset_name, column_id, column_name
    else:
        return None

# Load a json file and modify the dataset attribute
def modify_dataset(json_file,header_file, source = 'null'):
    with open(json_file, "r") as file:
        data = json.load(file)

    s_dict = {}
    if source != 'null':
        with open(source, "r") as source_file:
            ss = source_file.readlines()
        for line in ss:
            file_name, s = line.strip('\n').split(', ')
            s_dict[file_name] = s


    for entry in data:
        # check data_annotations field is not empty
        if entry["data_annotations"]:
            print(entry["data_annotations"])
            new_dataannotations = []
            #iter through the list of data_annotations
            for data_annotation in entry["data_annotations"]:
                # data_annotation is not empty
                if data_annotation:
                    dataset_name = data_annotation[0]
                    column_name = data_annotation[1]
                    result = find_column_info(dataset_name, column_name, header_file)
                    if result:
                        if source != 'null':
                            result = result, s_dict[dataset_name]
                        new_dataannotations.append(result)
            entry["data_annotations"] = new_dataannotations

    with open(json_file, "w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    modify_dataset('/Users/chunwei/research/mitaskem/demos/2023-04/mit-extraction.json',
                   '/Users/chunwei/research/mitaskem/resources/dataset/ensemble/headers.txt',
                   '/Users/chunwei/research/mitaskem/resources/dataset/ensemble/catalog.txt')
    # result = find_column_info('usafacts_hist.csv', 'Deaths', '../../../resources/dataset/headers.txt')
    # print(result)