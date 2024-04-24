import os
from typing import List, Dict
from commons.GitHubApi import GitHubRESTAPI
from commons.IOUtils import read_input_file
from commons.DataProcessor import DataProcessor

def get_modified_files(owner: str, repo: str, pr_number: str) -> tuple:
    """
    Identifies the modified files and the moved files of a given pull request and returns only the Java files.
    If any file has changed its name or path, it saves both the old and new names.

    Args:
        pr_number (str): The pull request number.
        repo (str): The name of the repository.
        owner (str): The owner of the repository.

    Returns:
        tuple: A tuple containing the changed files(List[str]) and the moved files List[Dict]
        List[str]: A list of strings representing the names of the modified Java files, including both old and new names if applicable.
    """

    gitApi = GitHubRESTAPI()

    print(f"retrieving files for PR {pr_number} of {repo}")

    files = gitApi.get_pull_request_changed_files(owner, repo, pr_number)
    changed_files = set()
    moved_files = []

    for file in files:
        filename = file["filename"]

        # Checks old and new names of the files that were moved
        if ("previous_filename" in file):
            previous_filename = file["previous_filename"]
            if previous_filename.endswith(".java") and filename.endswith(".java"):
                moved_files.append({ "old_filename": previous_filename, "new_filename": filename })


        # Only add java files
        if filename.endswith(".java"):
            changed_files.add(filename)

        # if filename was changed, then save both values
        if ("previous_filename" in file):
            previous_filename = file["previous_filename"]
            if previous_filename.endswith(".java"):
                changed_files.add(previous_filename)

    return list(changed_files), moved_files

def process_prs(file_path: str) -> List[Dict]:
    """
    Processes pull requests stored in a JSON file and identifies the changed files in each pull request,
    filtering out PRs that do not modify any Java files.

    Args:
        file_path (str): The path to the input JSON file containing pull request data.

    Returns:
        List[Dict]: A list of processed pull requests with identified changed files.

    Raises:
        FileNotFoundError: If the specified input file does not exist.
    """
    repo = os.path.basename(file_path).removesuffix(".json")

    prs = read_input_file(file_path)
    processed_prs = []

    for pr in prs:
        pr_number = pr["pr_number"]
        
        changed_files, moved_files = get_modified_files(OWNER, repo, pr_number)

        # Filter PRs with no Java changed files
        if len(changed_files) == 0:
            continue

        pr["changed_files"] = changed_files
        pr["moved_files"] = moved_files
        processed_prs.append(pr)
    
    return processed_prs

OWNER = "apache"
INPUT_DIRECTORY = "./2-PRs_Processing/2.3-Filter_PRs_with_Pulls/Output"
OUTPUT_DIRECTORY = "./2-PRs_Processing/2.4-Check_Changed_Files/Output"

DataProcessor.process_files(INPUT_DIRECTORY, OUTPUT_DIRECTORY, process_prs)