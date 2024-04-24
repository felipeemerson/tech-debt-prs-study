import json
from typing import List, Dict, Union

def read_input_file(input_file: str) -> Union[dict, List[Dict]]:
    """
    Reads data from an input file.

    Args:
        input_file (str): The path to the input file.

    Returns:
        list or dict: The data read from the input file.
    """
    with open(input_file, "r") as f:
        return json.load(f)

def write_output_file(output_file: str, data: Union[dict, List[Dict]]) -> None:
    """
    Writes data to an output file.

    Args:
        output_file (str): The path to the output file.
        data (list or dict): The data to write to the output file.
    """
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)