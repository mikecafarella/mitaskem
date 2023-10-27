from mitaskem.src import connect
import os

if __name__ == "__main__":
    with open("./data_sample/covid_deaths_usafacts.csv", "r") as f:
        csv = f.read()
    GPT_KEY = os.environ.get('OPENAI_API_KEY')
    res, yes = connect.dataset_header_dkg(csv, GPT_KEY)
    print(res)
