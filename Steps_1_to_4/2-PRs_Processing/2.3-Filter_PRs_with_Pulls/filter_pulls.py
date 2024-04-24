from typing import List, Dict
from commons.IOUtils import read_input_file
from commons.DataProcessor import DataProcessor

def filter_prs_with_pull(pr: dict) -> tuple:
    """
    Filters pull requests to remove those with pull commits, but preserving PRs with a single pull commit being the last one,
    in this case it removes only the pull commit and retain the remaining commits.

    Args:
        pr (dict): A dictionary representing a pull request with its associated commits.

    Returns:
        tuple: A tuple containing a boolean indicating whether the pull request is valid after filtering
            and the filtered pull request dictionary.
    """

    commits = pr["commits"]
    n_commits = len(commits)
    index = 0
    
    while index < n_commits - 1:
        is_pull = commits[index]["is_pull"]

        if is_pull:
            return False, None
        
        index += 1

    last_commit = commits[-1]
    
    if last_commit["is_pull"]:
        if last_commit["sha"] == pr["pr_commit"]: # In this case there is no commit to analyze
            return False, None
        
        pr["commits"] = commits[:-1] # Removes last commit because is pull

    return True, pr

def filter_prs(file_path: str) -> List[Dict]:
    """
    Filters pull requests in the JSON file to remove the PRs with pull commits while preserving pull requests
    with a single pull commit being the last one, in this case it removes only the pull commit and retain the remaining commits.

    This function iterates over each PR of the file.
    It reads the file, filters the pull requests using the `filter_prs_with_pull` function,
    and returns the filtered results as list.

    Args:
        file_path (str): The path to the input file containing pull requests data.
    
    Returns:
        List[Dict]: A list of filtered pull requests.

    Raises:
        FileNotFoundError: If the specified input directory does not exist.
    """
    prs = read_input_file(file_path)
    filtered_prs = []

    for pr in prs:
        is_valid, filtered_pr = filter_prs_with_pull(pr)

        if is_valid:
            filtered_prs.append(filtered_pr)

    return filtered_prs

INPUT_DIRECTORY = "./2-PRs_Processing/2.2-Identify_PR_Commit/Output"
OUTPUT_DIRECTORY = "./2-PRs_Processing/2.3-Filter_PRs_with_Pulls/Output"

DataProcessor.process_files(INPUT_DIRECTORY, OUTPUT_DIRECTORY, filter_prs)