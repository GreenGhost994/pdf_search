from json import dump, load
from os.path import isfile

def dump_data(results: dict, file_name: str) -> None:
    file_path = file_name+'.json'
    with open(file_path, 'w', encoding ='utf8') as json_file:
        dump(results, json_file, allow_nan=True, indent=4)

def load_data(file_name: str):
    file_path = file_name+'.json'
    if isfile(file_path):
        with open(file_path) as user_file:
            results=load(user_file)
        return results
    else:
        return {}

def update_data(file_name: str, **kwargs):
    results = load_data(file_name)

    for k, v in kwargs.items():
        results[k] = v

    dump_data(results, file_name)


def search_data(search_string: str, type: str) -> list:
    data = load_data('data')
    result = []

    if type == 'exact':
        for key, value in data.items():
            if search_string in value:
                result.append(key)
    elif type == 'included':
        for key, value in data.items():
            for i in value:
                if search_string in i:
                    result.append(key)
    result = list(set(result))
    return result