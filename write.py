"""
This module exports two functions: `write_to_csv` and `write_to_json`, each of
which accept an `results` stream of close approaches and a path to which to
write the data.

These functions are invoked by the main module with the output of the `limit`
function and the filename supplied by the user at the command line. The file's
extension determines which of these functions is used.
"""
import csv
import json
from pathlib import Path

# Paths to the root of the project.
PROJECT_ROOT = Path(__file__).parent.resolve()

def write_to_csv(ca_data, filename):
    """
    iterable of `CloseApproach` objects to a CSV file.

    The precise output specification is in `README.md`. Roughly, each output row
    corresponds to the information in a single close approach from the `results`
    stream and its associated near-Earth object.

    :param data: CloseApproach objects.
    :param filename: path to where data to be saved.
    """
    fieldnames = ('datetime_utc', 'distance_au', 'velocity_km_s', 'designation', 'name', 'diameter_km', 'potentially_hazardous')
  
    if filename is None:
        filename = 'CloseApproach.csv'  
   
    # Open the file and prepare the CSV writer
    with open(filename, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for line in ca_data:
            # Serialize both the CloseApproach and the NEO
            approach_data = line.serialize()
            neo_data = line.neo.serialize()
            
            # Combine the dictionaries and process fields
            content = {**approach_data, **neo_data}
            content["name"] = content.get("name", "")
            content["potentially_hazardous"] = "True" if content.get("potentially_hazardous", False) else "False"
            
            # Write the row to the CSV file
            writer.writerow(content)

def write_to_json(ca_data, filename):
    """ 
    iterable of `CloseApproach` objects to a JSON file.

    The precise output specification is in `README.md`. Roughly, the output is a
    list containing dictionaries, each mapping `CloseApproach` attributes to
    their values and the 'neo' key mapping to a dictionary of the associated
    NEO's attributes.

    :param data: CloseApproach objects.
    :param filename: path to where data to be saved.
    """
    
    if filename is None:
        filename = 'CloseApproach.json'  # Or some other default path

    data = [
        {
            "datetime_utc": line.serialize().get("datetime_utc", ""),
            "distance_au": line.serialize().get("distance_au", 0.0),
            "velocity_km_s": line.serialize().get("velocity_km_s", 0.0),
            "neo": {
                "designation": line.neo.serialize().get("designation", ""),
                "name": line.neo.serialize().get("name", ""),
                "diameter_km": line.neo.serialize().get("diameter_km", float('nan')),
                "potentially_hazardous": line.neo.serialize().get("potentially_hazardous", False)
            }
        }
        for line in ca_data
    ]

    # Write the data to the JSON file
    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)

