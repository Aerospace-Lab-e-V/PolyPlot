import json

def import_json(filename):
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            config = json.load(file)

        if config.get('version',None) == 3:
            return defaults(config)
        else:            
            raise ValueError("wrong .json format")
    except FileNotFoundError:
        print(f"{filename} does not exist. please verify the name and position of your config.json")
        raise



def defaults(config):
    for dataframe in config.get('dataframes',[]):
        dataframe['material_colors']['default'] = dataframe['material_colors'].get('default', "#333333")


    return config