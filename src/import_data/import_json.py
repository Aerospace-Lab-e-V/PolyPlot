import json

def import_json(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        config = json.load(file)

    if config.get('version',None) == 3:
        return defaults(config)
    else:            
        raise ValueError("wrong .json format")



def defaults(config):
    for dataframe in config.get('dataframes',[]):
        dataframe['material_colors']['default'] = dataframe['material_colors'].get('default', "#333333")


    return config