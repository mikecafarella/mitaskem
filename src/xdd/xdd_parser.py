# Client code for SKEMA TR
import argparse
import io
import json
import time
from typing import List, Union, BinaryIO, Callable
from typing import Optional, Dict, Any
from zipfile import ZipFile

import pandas as pd
import requests
from fastapi import APIRouter, FastAPI, UploadFile, Response, status

COSMOS_ADDRESS = "https://xdd.wisc.edu/cosmos_service"
router = APIRouter()


# Utility code for the endpoints

def annotate_with_skema(
        endpoint: str,
        input_: Union[str, List[str], List[Dict], List[List[Dict]]]) -> List[Dict[str, Any]]:
    """ Blueprint for calling the SKEMA-TR API """

    if isinstance(input_, (str, dict)):
        payload = [
            input_
        ]  # If the text to annotate is a single string representing the contents of a document, make it a list with
        # a single element
    else:
        payload = input_  # if the text to annotate is already a list of documents to annotate, it is the payload itself
    response = requests.post(endpoint, json=payload, timeout=600)
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(
            f"Calling {endpoint} failed with HTTP code {response.status_code}"
        )



def parquet_to_json(path):
    parquet_df = pd.read_parquet(path)
    parquet_json = parquet_df.to_json()
    parquet_data = json.loads(parquet_json)

    if len(parquet_data) > 0:
        parquet_data_keys = list(parquet_data.keys())
        num_data_rows = max(
            [int(k) for k in parquet_data[parquet_data_keys[0]]]
        )

        row_order_parquet_data = [dict() for i in range(num_data_rows + 1)]
        for field_key, row_data in parquet_data.items():
            for row_idx, datum in row_data.items():
                row_idx_num = int(row_idx)
                row_order_parquet_data[row_idx_num][field_key] = datum

        # if filename == "documents.parquet":
        # Sorts the content sections by page number and then by
        # bounding box location. Use x-pos first to account for
        # multi-column documents and then sort by y-pos.
        row_order_parquet_data.sort(
            key=lambda d: (
                d["page_num"],
                d["bounding_box"][0]
                // 500,  # allows for indentation while still catching items across the center line
                # (d["bounding_box"][0]) // 100
                # + round((d["bounding_box"][0] % 100 // 10) / 10),
                d["bounding_box"][1],
            )
        )

        edits = list()
        for e1, extraction1 in enumerate(row_order_parquet_data):
            (ext1_x1, ext1_y1, ext1_x2, ext1_y2) = extraction1[
                "bounding_box"
            ]
            # Don't bother processing for left-justified or centered
            # content ... only right column content needs to be checked
            if ext1_x1 < 500:
                continue

            ext1_page_num = extraction1["page_num"]
            found_col_break = False
            insertion_index = -1
            t1 = e1
            while t1 > 0:
                extraction2 = row_order_parquet_data[t1 - 1]
                ext2_page_num = extraction2["page_num"]
                # If the previous sorted entry is on an earlier page
                # then we can stop our search
                if ext1_page_num > ext2_page_num:
                    break

                (ext2_x1, ext2_y1, ext2_x2, ext2_y2) = extraction2[
                    "bounding_box"
                ]

                if ext1_y2 <= ext2_y1:
                    ext2_xspan = ext2_x2 - ext2_x1
                    # Useful heuristic cutoff for now
                    if ext2_xspan >= 800:
                        found_col_break = True
                        insertion_index = t1 - 1
                t1 -= 1
            if found_col_break:
                edits.append(
                    {
                        "del_idx": e1,
                        "ins_idx": insertion_index,
                        "val": extraction1,
                    }
                )
        for edit_dict in edits:
            del row_order_parquet_data[edit_dict["del_idx"]]
            row_order_parquet_data.insert(
                edit_dict["ins_idx"], edit_dict["val"]
            )
        row_order_parquet_data.sort(key=lambda d: (d["pdf_name"]))

        name2results = dict()
        for row_data in row_order_parquet_data:
            if row_data["pdf_name"] in name2results:
                name2results[row_data["pdf_name"]].append(row_data)
            else:
                name2results[row_data["pdf_name"]] = [row_data]

        return next(iter(name2results.items()))[1]


def cosmos_client(name: str, data: BinaryIO):
    """
    Posts a pdf to COSMOS and returns the JSON representation of the parquet file

    """

    # Create POST request to COSMOS server
    # Prep the pdf data for upload
    files = [
        ("pdf", (name, data, 'application/pdf')),
    ]
    print(f"Sending {name} to COSMOS")
    response = requests.post(f"{COSMOS_ADDRESS}/process/", files=files)
    print(f"Received response from COSMOS: {response.status_code}")

    if response.status_code == status.HTTP_202_ACCEPTED:

        callback_endpoints = response.json()

        for retry_num in range(200):
            time.sleep(3)  # Retry in ten seconds
            poll = requests.get(f"{COSMOS_ADDRESS}{callback_endpoints['status_endpoint']}")
            print(f"Polling COSMOS on retry num {retry_num + 1}")
            if poll.status_code == status.HTTP_200_OK:
                poll_results = poll.json()
                # If the job is completed, fetch the results
                if poll_results['job_completed']:
                    cosmos_response = requests.get(f"{COSMOS_ADDRESS}{callback_endpoints['result_endpoint']}")
                    if cosmos_response.status_code == status.HTTP_200_OK:
                        data = cosmos_response.content
                        with ZipFile(io.BytesIO(data)) as z:
                            for file in z.namelist():
                                if file.endswith(".parquet") and \
                                        not file.endswith("_figures.parquet") and \
                                        not file.endswith("_pdfs.parquet") and \
                                        not file.endswith("_tables.parquet") and \
                                        not file.endswith("_sections.parquet") and \
                                        not file.endswith("_equations.parquet"):
                                    # convert parquet to json
                                    with z.open(file) as zf:
                                        json_data = parquet_to_json(zf)
                                        #print file name and json data in the same line with a nice formatting
                                        print(f"{file} : {json_data}")
                                        return json_data
                        # Shouldn't reach this point
                        raise RuntimeError("COSMOS data doesn't include document file for annotation")

                    else:
                        raise RuntimeError(
                            f"COSMOS Result Error - STATUS CODE: {response.status_code} - {COSMOS_ADDRESS}")
                # If not, just wait until the next iteration
                else:
                    pass

        # If we reached this point, we time out
        raise TimeoutError(f"Timed out waiting for COSMOS on retry num {retry_num + 1}")

    else:
        raise RuntimeError(f"COSMOS Error - STATUS CODE: {response.status_code} - {COSMOS_ADDRESS}")

def main(file_path):
    # Open the file in binary mode
    with open(file_path, "rb") as file:
        # Call the cosmos_client function
        cosmos_client("Flamingo.pdf", file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a PDF file.')
    parser.add_argument('--file', type=str, default="/Users/chunwei/Documents/paper/LLM/Flamingo.pdf",
                        help='The path to the PDF file to process.')
    args = parser.parse_args()
    main(args.file)