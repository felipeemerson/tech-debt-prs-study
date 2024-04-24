from typing import List, Dict
from commons.IOUtils import read_input_file
from commons.DataProcessor import DataProcessor

def identify_commit_before_pr_commit(pr: dict) -> dict:
    """
    Identifies the commit that precedes the PR commit.

    This function examines the commits associated with a pull request (PR) and determines the commit that comes before
    the PR commit. There are two scenarios:
    (i) If there is a commit preceding the PR commit in the PR's commits, then that commit is considered the preceding commit.
    (ii) If the PR commit is the first commit in the PR's commits, then it considers the concept of a commit's parent.
         If the PR commit has only one parent, then that parent commit is considered the preceding commit. Otherwise, the PR is discarded (returns None).

    Args:
        pr (dict): A dictionary representing the pull request.

    Returns:
        dict: The input dictionary with an additional key "start_commit" representing the commit preceding the PR commit,
              and a key "is_pr_commit_first" indicating whether the PR commit is the first commit in the PR's commits.

    Returns None if the PR commit is the first commit and has multiple parents.
    """

    pr_commit = pr["pr_commit"]
    commits = pr["commits"]

    is_pr_commit_first = pr["commits"][0]["sha"] == pr_commit

    if is_pr_commit_first:
        start_commit = None

        # Set start commit to be the PR commit parent
        for commit in commits:
            if commit["sha"] == pr_commit:
                parents = commit["parents"]

                if len(parents) == 1:
                    start_commit = parents[0]["node"]["oid"]

        if start_commit is None:
            return None

        pr["start_commit"] = start_commit

    else:
        # Search for the commit before PR commit
        for index in range(len(commits)): 
            if commits[index]["sha"] == pr_commit:
                start_commit = commits[index - 1]["sha"]
                pr["start_commit"] = start_commit

    pr["is_pr_commit_first"] = is_pr_commit_first

    # Removes parents entry as it will no longer be used
    for commit in commits:
        del commit["parents"]

    pr["commits"] = commits
    return pr

def process_prs(file_path: str) -> List[Dict]:
    """
    Processes pull requests stored in JSON files within a directory and identifies the commit preceding the PR commit.

    This function reads pull request data from a JSON file specified by the input file path.
    For each pull request, it identifies the commit that precedes the PR commit using the `identify_commit_before_pr_commit` function.
    If the PR commit has more than one parent, it skips that PR.
    Finally, it returns a list of dictionaries containing the processed pull requests.

    Args:
        file_path (str): The path to the input JSON file containing pull request data.

    Returns:
        List[Dict]: A list of dictionaries representing the processed pull requests.

    """

    prs = read_input_file(file_path)
    processed_prs = []

    for pr in prs:
        current_processed_pr = identify_commit_before_pr_commit(pr)

        # If PR commit has more than one parent it returns None and skip the PR
        if current_processed_pr is not None:
            processed_prs.append(current_processed_pr)

    return processed_prs


INPUT_DIRECTORY = "./2-PRs_Processing/2.4-Check_Changed_Files/Output"
OUTPUT_DIRECTORY = "./2-PRs_Processing/2.5-Identify_Start_Commit/Output"

DataProcessor.process_files(INPUT_DIRECTORY, OUTPUT_DIRECTORY, process_prs)