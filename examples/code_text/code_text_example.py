import requests


def main():
    path="http://localhost:8000/code_text/run"
    with open("code.py", "r") as f:
        code = f.read()
    with open("text.txt", "r") as f:
        text = f.read()

    gpt_key = "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"

    dict= {"input_code": code, "input_text": text, "gpt_key": gpt_key}

    r = requests.post(path, params=dict)
    print(r.text)

if __name__ == "__main__":
    main()