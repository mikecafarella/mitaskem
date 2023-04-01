import json

# Load JSON files
with open("extractions/mit_extraction.json", "r") as file_a:
    data_a = json.load(file_a)

with open("extractions/arizona_extraction.json", "r") as file_b:
    data_b = json.load(file_b)

# Load mapping file
with open("extractions/mapping.txt", "r") as mapping_file:
    mappings = mapping_file.readlines()

# Parse the mappings into a dictionary
mapping_dict = {}
for mapping in mappings:
    key, value = mapping.strip().split(": ")
    mapping_dict[key] = value.strip('"').strip(",")


# Iterate through data_b and append the corresponding entry from data_a if there's a mapping
for entry_b in data_b:
    entry_b_id = entry_b["id"]
    print(entry_b_id)
    if entry_b_id in mapping_dict.values():
        print("Found mapping")
        # Get the corresponding key (id from data_a) and find the entry in data_a
        entry_a_id = [k for k, v in mapping_dict.items() if v == entry_b_id][0]
        for entry_a in data_a:
            if entry_a["id"] == entry_a_id:
                entry_b["mit"] = entry_a
                break

# Save the updated data_b to a new JSON file
with open("extractions/ta1_bucky_extraction.json", "w") as file_b_updated:
    json.dump(data_b, file_b_updated, indent=4)