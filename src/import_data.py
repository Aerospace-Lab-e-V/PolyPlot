import requests
import json
import pandas as pd

url = "https://teable.aerospace-lab.de/api/table/tblFwalTJ3PyuZzyE43/record"

headers = {
    "Authorization": "Bearer teable_accEbwLnOPcALnjGJXU_Hp6iPPr5mn5WPOgMNfzqgAro1j9t1G0Vj6DjAJTMg+s=",
    "Accept": "application/json"
}

def import_teable(filter = None):
    params = {
        "viewId": "viw6Lttx16wtFhDAkbx",
        "filter": json.dumps(filter)
    }
    
    response = requests.get(url, params=params, headers=headers)
    print(response)
    # dataframe = pd.json_normalize(json.loads(response['results']))
    dataframe = pd.DataFrame.from_dict(response, orient='index')
    print(dataframe)
    return pandas