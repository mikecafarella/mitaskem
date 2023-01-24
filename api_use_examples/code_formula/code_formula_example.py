import requests


def main():
    path="http://localhost:8000/code_formula/run"
    with open("CHIME_SVIIvR.py", "r") as f:
        code = f.read()
    with open("formula.tex_idx", "r") as f:
        formula = f.read()

    gpt_key = "YOUR KEY HERE"

    dict= {"input_code": code, "input_formula": formula, "gpt_key": gpt_key}

    r = requests.post(path, params=dict)
    print(r.text)

if __name__ == "__main__":
    main()