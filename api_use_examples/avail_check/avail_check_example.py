import requests


def main():
    path="http://localhost:8000/avail_check/run"
    word = "blahblah"
    dict= {"input": word}

    r = requests.post(path, params=dict)
    print(r.text)

if __name__ == "__main__":
    main()