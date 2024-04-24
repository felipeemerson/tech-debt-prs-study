import os
import re
import pandas as pd
from commons.IOUtils import read_input_file
from typing import List, Dict

def prs_as_dict(prs: List[Dict]) -> dict:
    """
    Converts a list of pull requests (PRs) into a dictionary with PR numbers as keys.

    This method converts a list of pull requests (PRs), represented as dictionaries,
    into a dictionary where the keys are the PR numbers and the values are the corresponding PR dictionaries.

    Args:
        prs (List[Dict]): A list of pull requests, where each pull request is represented as a dictionary.

    Returns:
        dict: A dictionary where the keys are PR numbers and the values are the corresponding PR dictionaries.
    """

    prs_dict = {}

    for pr in prs:
        prs_dict[pr["node"]["number"]] = pr

    return prs_dict

PRS_INPUT_DIRECTORY = "./2-PRs_Processing/2.1-Filter_PRs_by_Merged_Date/Output"
ISSUES_DIRECTORY = "./3-SonarQube_Execution/Output"
OUTPUT_DIRECTORY = "./4-Post_Processing/4.3-PRs_Characterization_Processing/Output"

processed_prs = []

for dirpath, dirnames, filenames in os.walk(ISSUES_DIRECTORY):
  
  current_repo = ""
  prs = {}

  for file in filenames:
    current_issues = read_input_file(f"{ISSUES_DIRECTORY}/{file}")

    match = re.match(r'issues_(.*)_(\d+).json', file)

    repo = match.group(1)
    pr_number = int(match.group(2))

    print(f"processing repo {repo} pr {pr_number}")

    if repo != current_repo:
        prs_list = read_input_file(f"{PRS_INPUT_DIRECTORY}/{repo}.json")
        prs = prs_as_dict(prs_list)
        current_repo = repo

    current_pr_data = prs[pr_number]["node"]

    processed_prs.append({
        "pr_number": pr_number,
        "repo": repo,
        "created_at": current_pr_data["createdAt"],
        "merged_at": current_pr_data["mergedAt"],
        "additions": current_pr_data["additions"],
        "deletions": current_pr_data["deletions"],
        "changed_files_count": current_pr_data["changedFiles"],
        "commits_count": current_pr_data["commits"]["totalCount"]
    })

df = pd.DataFrame(processed_prs)
df.to_csv(f"{OUTPUT_DIRECTORY}/prs_characterization.csv", header=True, index=False)