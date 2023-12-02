import json
import os
from datetime import datetime

def create_json_file(file_path):
    """
    Creates an empty JSON file.

    Parameters:
    - file_path (str): The path to the JSON file.
    """
    with open(file_path, "w") as json_file:
        json.dump({}, json_file)
    print(f"JSON file '{file_path}' created.")

def get_info_from_json(file_path, variable_name):
    """
    Read data from a JSON file and return information based on the specified key.

    Parameters:
    - json_file_path (str): Path to the JSON file.
    - key (str): Key to extract information from the JSON data.

    Returns:
    - Information corresponding to the specified key, or None if the key is not found.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    return data.get(variable_name)

def add_info_to_json(file_path, variable_name, data):
    """
    Adds information to a JSON file. Each entry is associated with the variable name and the current date.

    Parameters:
    - file_path (str): The path to the JSON file.
    - variable_name (str): The name of the variable.
    - data (any): The information to be added.
    """
    with open(file_path, "r+") as json_file:
        # Load existing data from the file
        existing_data = json.load(json_file)

        # Add new entry with current date
        existing_data[variable_name] = data#{"date": current_date, "data": data}

        # Rewind the file and write the updated data
        json_file.seek(0)
        json.dump(existing_data, json_file, indent=2)
        json_file.truncate()
    print(f"Information added to '{variable_name}' in '{file_path}'.")

def delete_info_from_json(file_path, variable_name):
    """
    Deletes information associated with a variable from a JSON file.

    Parameters:
    - file_path (str): The path to the JSON file.
    - variable_name (str): The name of the variable whose information is to be deleted.
    """
    with open(file_path, "r+") as json_file:
        # Load existing data from the file
        existing_data = json.load(json_file)

        # Remove the entry associated with the variable name
        if variable_name in existing_data:
            del existing_data[variable_name]

            # Rewind the file and write the updated data
            json_file.seek(0)
            json.dump(existing_data, json_file, indent=2)
            json_file.truncate()
            print(f"Information deleted for '{variable_name}' in '{file_path}'.")
        else:
            print(f"No information found for '{variable_name}' in '{file_path}'.")

def remove_json_file(file_path):
    """
    Removes a JSON file.

    Parameters:
    - file_path (str): The path to the JSON file.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"JSON file '{file_path}' removed.")
    else:
        print(f"No JSON file found at '{file_path}'.")


import json

def fetch_data_from_json(file_path, variable_name):
    """
    Fetches data associated with a variable from a JSON file.

    Parameters:
    - file_path (str): The path to the JSON file.
    - variable_name (str): The name of the variable.

    Returns:
    - dict: The data associated with the variable, or an empty dictionary if the variable is not found.
    """
    try:
        # Open the JSON file in read mode
        with open(file_path, "r") as json_file:
            # Load existing data from the file
            existing_data = json.load(json_file)

            # Fetch data associated with the variable name
            data = existing_data.get(variable_name, {})

            return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


# Example usage:
json_file_path = "example_data.json"

create_json_file(json_file_path)
city = "Zurich"
add_info_to_json(json_file_path, "fromCity", city)

# Example usage:
json_file_path = "example_data.json"
variable_name_to_fetch = "variable1"

data_fetched = fetch_data_from_json(json_file_path, variable_name_to_fetch)

if data_fetched:
    print(f"Data for '{variable_name_to_fetch}': {data_fetched}")
else:
    print(f"No data found for '{variable_name_to_fetch}' in '{json_file_path}'.")

#delete_info_from_json(json_file_path, "variable1")
#remove_json_file(json_file_path)

