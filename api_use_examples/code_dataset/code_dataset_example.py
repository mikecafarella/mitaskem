import requests


def main():
    path="http://localhost:8000/code_dataset/run"
    with open("bucky_sample.py", "r") as f:
        code = f.read()

    datasets = "./model/Bucky/data_sample/"

    gpt_key = "YOUR KEY HERE"

    dict= {"input_code": code, "input_dataset": datasets, "gpt_key": gpt_key}

    print("About to send the post request")
    r = requests.post(path, params=dict)
    print(r.text)

if __name__ == "__main__":
    main()