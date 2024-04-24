from datetime import datetime
from typing import List, Dict
from commons.IOUtils import read_input_file
from commons.DataProcessor import DataProcessor

def filter_prs(file_path: str) -> List[Dict]:
    """
    Reads PRs from a file, filters them by merge date,
    and keeps all PRs whose merge was done by February 29, 2024, 23:59:59.

    Args:
        file_path (str): Path to the file containing PRs.

    Returns:
        List[Dict]: List of filtered PRs.
    """
    
    prs = read_input_file(file_path)

    filtered_prs = []

    for pr in prs:
        merged_date = pr["node"]["mergedAt"]

        merged_date_as_dt = datetime.strptime(merged_date, "%Y-%m-%dT%H:%M:%SZ")
        limit_date = datetime(2024, 2, 29, 23, 59, 59) # 2024-02-29 23:59:59

        if merged_date_as_dt <= limit_date:
            filtered_prs.append(pr)
        
    return filtered_prs

INPUT_DIRECTORY = "./1-PRs_Mining/Output"
OUTPUT_DIRECTORY = "./2-PRs_Processing/2.1-Filter_PRs_by_Merged_Date/Output"

DataProcessor.process_files(INPUT_DIRECTORY, OUTPUT_DIRECTORY, filter_prs)

