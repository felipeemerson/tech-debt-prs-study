import pytz
from datetime import datetime
from typing import List, Dict
from commons.IOUtils import read_input_file
from commons.DataProcessor import DataProcessor

def format_date(date: str) -> datetime:
    """
    Converts a date and time string to a datetime object in UTC.

    Args:
        date (str): A string representing the date and time in ISO 8601 format.

    Returns:
        datetime: A datetime object representing the converted date and time in UTC.
    """

    if date.endswith("Z"):
        date = date[:-1]  # Removes 'Z'

    date_time = datetime.fromisoformat(date)
    date_time = date_time.replace(tzinfo=pytz.utc)

    return date_time

def is_pull_commit(total_parents: int) -> bool:
    """
    Checks if a commit in a pull request has more than one parent, indicating it's a pull commit.

    Args:
        total_parents (int): The total number of parents for the commit.

    Returns:
        bool: True if the commit has more than one parent (is a pull commit), False otherwise.
    """
    return total_parents > 1


def identify_pr_commit(pr: dict) -> dict:
    """
    Processes the commits associated with a pull request.

    Args:
        pr (dict): A dictionary containing information about the pull request.

    Returns:
        dict: A dictionary containing processed information about the pull request,
            including the PR number, creation date, information about each commit,
            and the SHA of the PR commit (the commit that opened the pull request).

    This function identifies the PR commit, which is the commit that opened the pull request,
    based on the commit with the most recent date before the pull request's creation date.
    For each commit, it also checks if it's a pull commit (a commit resulting from a merge operation),
    which occurs when the total number of parents for the commit is greater than 1.
    """
    pr_number = pr['node']['number']
    pr_created_at = format_date(pr['node']['createdAt'])

    commits = pr['node']['commits']['nodes']
    commits_processed = []
    pr_commit = None

    # Iterate through each commit associated with the pull request
    for commit in commits:
        sha = commit['commit']['oid']
        parents = commit['commit']['parents']['edges']
        total_parents = len(parents)
        created_at = commit['commit']['committer']['date']
        created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S%z")

        # Determine if the commit is the PR commit based on its creation date
        if created_at < pr_created_at:
            pr_commit = sha

        commits_processed.append({
            'sha': sha,
            'created_at': str(created_at),
            'is_pull': is_pull_commit(total_parents),
            'parents': parents
        })

    return {
        'pr_number': pr_number,
        'created_at': str(pr_created_at),
        'commits': commits_processed,
        'pr_commit': pr_commit
    }

def process_prs(file_path: str) -> List[Dict]:
    """
    Processes pull requests stored in the JSON file and identifies the pull request commits.

    This function iterates over each PR in the specified file containing pull requests data.
    For each file, it reads the pull request data, identifies the pull request commits using the `identify_pr_commit` function,
    and returns the processed results as list.

    Args:
        file_path (str): The path to the input file containing pull requests data.

    Returns:
        List[Dict]: A list of processed pull requests, each PR includes the PR number, creation date, information about each commit,
            and the SHA of the PR commit (the commit that opened the pull request).

    Raises:
        FileNotFoundError: If the specified input directory does not exist.
    """

    prs = read_input_file(file_path)
    processed_prs = []

    for pr in prs:
        current_processed_pr = identify_pr_commit(pr)

        # Skip PRs with None PR commit
        if current_processed_pr["pr_commit"] is None:
            continue
    
        processed_prs.append(current_processed_pr)
    
    return processed_prs

INPUT_DIRECTORY = "./2-PRs_Processing/2.1-Filter_PRs_by_Merged_Date/Output"
OUTPUT_DIRECTORY = "./2-PRs_Processing/2.2-Identify_PR_Commit/Output"

DataProcessor.process_files(INPUT_DIRECTORY, OUTPUT_DIRECTORY, process_prs)