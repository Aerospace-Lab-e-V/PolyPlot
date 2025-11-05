import requests
import os
import json
import pandas as pd

def collums_list(columns, layers):  # returns a list of all columns that should be requested via API
    wanted_fields = []

    for layer in range(len(layers) -1):
        wanted_fields.append(layers[layer]["name"])
    for axes in columns:
        for column in axes:
            wanted_fields.append(column + " low" )
            wanted_fields.append(column + " high")

    return wanted_fields



def import_teable(teable_url, api_key, columns, layers, filter):
    wanted_fields = collums_list(columns, layers)

    params = {
        "take": 1000,
        "skip": 0,
        "filter": json.dumps(filter),
        "fields": wanted_fields
    }
    url = teable_url

    headers = {
        "Authorization": api_key,
        "Accept": "application/json"
    }


    status = requests.head(url, headers=headers)

    if status.status_code == 200:
        data = []
        print("importing...")
        while True:            
            response = requests.get(url, params=params, headers=headers).json()
            records = [rec["fields"] for rec in response["records"]]

            if not records:
                break

            params["skip"] += params["take"] 

            data.extend(records)
        dataframe = pd.DataFrame(data, columns=wanted_fields)        # & raise error if _low or layer column not found

        # print(dataframe)
        print(f"data received successfully  (Total of {len(data)} points)")  
  
        return dataframe
    elif status == 403:
        raise PermissionError("ERROR 403 - Teable API: kein Zugriffsrecht. Bitte API Key & URL prüfen")
    else:
        raise Exception(f"unknown Teable error {status.status_code}: {status.text}")



def import_excel(import_file_name, import_sheet):      # & filter 
    data = pd.read_excel(
        os.path.join(
            os.getcwd(),
            'material_properties',
            import_file_name,
            ),
        sheet_name = import_sheet
    )
    return data


def import_json(finename):
    with open('config.json', 'r', encoding="utf-8") as file:
        config = json.load(file)

    version = config['version']
    if version == 1:
        return config['frames']
    elif version == 2:
        frames = {}
        for dataset in config['datasets']:
            frames.append(parse_json_v2(dataset))
        return frames
            

def parse_json_v2(frame):
    pass