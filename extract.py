"""
Extract data on near-Earth objects and close approaches from CSV and JSON files.

The `load_neos` function extracts NEO data from a CSV file, formatted as
described in the project instructions, into a collection of `NearEarthObject`s.

The `load_approaches` function extracts close approach data from a JSON file,
formatted as described in the project instructions, into a collection of
`CloseApproach` objects.

The main module calls these functions with the arguments provided at the command
line, and uses the resulting collections to build an `NEODatabase`.
"""
import csv
import json

from models import NearEarthObject, CloseApproach


def load_neos(neo_csv_path):
    """
    Read near-Earth object information from a CSV file.

    :param neo_csv_path: A path to a CSV file containing data about near-Earth objects.
    :return: A collection of `NearEarthObject`s.
    """
    neo_list = []

    try:
        with open(neo_csv_path, mode='r') as file:
            csv_line = csv.DictReader(file)

            for row in csv_line:
                neObject = NearEarthObject(
                    name = row['name'] or None, 
                    designation=row['pdes'], 
                    diameter=row['diameter'],
                    hazardous= row['pha'] == 'Y',
                )
                neo_list.append(neObject)
                
    except Exception as ex:
        print(f"couldnt open/parse csv file bcz: {ex}")

    return neo_list if neo_list else None


def load_approaches(cad_json_path):
    """
    Read close approach data from a JSON file.

    :param neo_csv_path: A path to a JSON file containing data about close approaches.
    :return: A collection of `CloseApproach`es.
    """
    aproach_list = []
    try:
        with open(cad_json_path, mode='r') as file:
            json_data = json.load(file)

        #create dict w fields as key/data as value
        entry_dict = [dict(zip(json_data["fields"], value)) for value in json_data["data"]]

        for entry in entry_dict:
                 
            # Create CloseApproach instance
            apprObj = CloseApproach(
                designation = entry['des'],
                time = entry['cd'],
                distance = float(entry['dist']),  
                velocity = float(entry['v_rel'])
            )
            aproach_list.append(apprObj)
            
    except Exception as ex:
        print(f"couldnt open/parse json file bcz: {ex}")
         
    return aproach_list if aproach_list else None