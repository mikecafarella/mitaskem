from src import connect, gpt_key

if __name__ == "__main__":
    with open("./data_sample/covid_deaths_usafacts.csv", "r") as f:
        csv = f.read()
    res, yes = connect.dataset_header_dkg(csv, gpt_key.GPT_KEY)
    print(res)
