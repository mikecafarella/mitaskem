import os
import pandas as pd

DATASET_INFO = {
    "nychealth.csv": "NYC Health Covid data with 1011 rows x 67 columns",
    "covid_confirmed_usafacts.csv": "USA Covid confirmed cases with 3194 rows x 557 columns (truncated columns)",
    "covid_deaths_usafacts.csv": "USA Covid death cases with 3194 rows x 557 columns (truncated columns)",
    "covid_tracking.csv": "Covid tracking data with 20781 rows x 56 columns",
    "usafacts_hist.csv": "Fact Covid data (adm2) with 1800367 rows x 5 columns"
}
def print_df(dir):
    print("We have a set of datasets:")
    print("---------------------------------------")
    for filename in os.listdir(dir):
        if filename.endswith(".csv"):
            print(DATASET_INFO[filename]+". Schema and data sample:")
            df = pd.read_csv (os.path.join(dir, filename))
            print(df)
            print("---------------------------------------")


def get_df(dir):
    dfs = []
    for filename in os.listdir(dir):
        if filename.endswith(".csv"):
            df = pd.read_csv (os.path.join(dir, filename))
            dfs.append((DATASET_INFO[filename], df))
    return dfs