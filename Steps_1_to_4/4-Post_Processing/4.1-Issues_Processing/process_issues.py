import os
import re
import pandas as pd
from commons.IOUtils import read_input_file
from commons.SonarQubeApi import SonarQubeApi
from commons.SonarMetricsCollector import SonarMetricsCollector
from typing import List, Dict

def parse_debt(debt_as_string: str) -> int:
    """
    Parses debt returned by SonarQube into minutes.

    The debt can be in the format "Xmin" (where X is the number of minutes) or "XhYmin" (where X is the number
        of hours and Y is the number of minutes) or "XdYhZmin" (x working days, y hours and z minutes,
        with one working day equal to eight hours).

    Args:
        debt_as_string (str): A string representing debt in the format "XdYhZmin".

    Returns:
        int: The total debt in minutes.
    """

    debt_pattern = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)min)?')
    match = debt_pattern.match(debt_as_string)

    if not match:
        return None

    days = match.group(1)
    hours = match.group(2)
    minutes = match.group(3)

    days = int(days) if days else 0
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0

    total_min = days * 8 * 60 + hours * 60 + minutes
    return total_min

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
        prs_dict[pr["pr_number"]] = pr

    return prs_dict

def process_issues(repo, pr, issues):
    """
    Process the issues for a given pull request (PR) in a repository.

    This method processes the issues for a specific pull request (PR) in a repository.
    It extracts relevant information from the issues, such as rule, severity, file, type, status, debt, and metrics.
    Additionally, it determines whether an issue is old based on past issues encountered.

    Args:
        repo (str): The name of the repository.
        pr (dict): The pull request represented as a dictionary containing information such as PR number.
        issues (list): A list of dictionaries representing the issues reported by SonarQube.

    Returns:
        list: A list of dictionaries containing processed information about the issues.
    """

    pr_number = pr["pr_number"]

    init_raw_issues = issues[0]["issues"]["issues"]

    preexisting_issues = set([issue["key"] for issue in init_raw_issues])

    sonar_component = f"{repo}-{pr_number}"

    metrics = {}

    for execution in issues:
        current_metrics = execution["metrics"]

        for component in current_metrics:
            metrics[component] = current_metrics[component]

    last_issues = issues[-1]["issues"]["issues"]
    old_filename_moved_files = set([moved_files["old_filename"] for moved_files in pr["moved_files"]])

    current_processed_issues = []

    for issue in last_issues:
        issue_key = issue["key"]
        issue_status = issue["status"]
        issue_severity = issue["severity"]
        issue_type = issue["type"]
        issue_rule = issue["rule"]
        issue_debt = parse_debt(issue["debt"])
        issue_file = issue["component"].replace(f"{sonar_component}:", "", 1)
        ncloc = metrics[issue["component"]]["ncloc"]
        complexity = metrics[issue["component"]]["complexity"]

        if issue_file in old_filename_moved_files: # skip old path of moved files, because it duplicates the issues in the new path
            continue

        current_processed_issues.append({
            "repo": repo,
            "pr_number": pr_number,
            "rule": issue_rule,
            "severity": issue_severity,
            "file": issue_file,
            "type": issue_type,
            "status": issue_status,
            "debt": issue_debt,
            "ncloc_affected_file": ncloc,
            "complexity": complexity,
            "origin": "PRE-EXISTING" if issue_key in preexisting_issues else "NEW"
        })

    return current_processed_issues

PRS_INPUT_DIRECTORY = "./2-PRs_Processing/2.5-Identify_Start_Commit/Output"
ISSUES_INPUT_DIRECTORY = "./3-SonarQube_Execution/Output"
OUTPUT_DIRECTORY = "./4-Post_Processing/4.1-Issues_Processing/Output"

sonar_api = SonarQubeApi(True)
metrics_collector = SonarMetricsCollector(sonar_api)
processed_issues = []

for dirpath, dirnames, filenames in os.walk(ISSUES_INPUT_DIRECTORY):
  
  current_repo = ""
  prs = {}

  for file in filenames:
    current_issues = read_input_file(f"{ISSUES_INPUT_DIRECTORY}/{file}")

    match = re.match(r'issues_(.*)_(\d+).json', file)

    repo = match.group(1)
    pr_number = int(match.group(2))

    print(f"processing repo {repo} pr {pr_number}")

    if repo != current_repo:
        prs_list = read_input_file(f"{PRS_INPUT_DIRECTORY}/{repo}.json")
        prs = prs_as_dict(prs_list)
        current_repo = repo

    current_processed_issues = process_issues(repo, prs[pr_number], current_issues)

    processed_issues.extend(current_processed_issues)


df = pd.DataFrame(processed_issues)
df.to_csv(f"{OUTPUT_DIRECTORY}/processed_issues.csv", header=True, index=False)