import io
import logging
import os
import requests
import shutil
import sys
import time
import traceback
import zipfile
from BuildHandler import BuildHandler
from commons.IOUtils import read_input_file, write_output_file
from commons.SonarQubeApi import SonarQubeApi
from commons.SonarMetricsCollector import SonarMetricsCollector
from ExecutionMonitor import ExecutionMonitor
from SonarQubeRunner import SonarQubeRunner
from typing import List, Dict

def setup_logger() -> logging.Logger:
    """
    Generates a logger responsible for logging all events during the executions.

    Returns:
        logging.Logger: The logger object for logging execution events.
    """
        
    logger = logging.getLogger("SonarQube-executions")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = logging.FileHandler("./3-SonarQube_Execution/logs/executions.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    sys_handler = logging.StreamHandler(sys.stdout)
    sys_handler.setFormatter(formatter)
    logger.addHandler(sys_handler)
    
    return logger

def create_exclude_prs_file(repo: str) -> None:
    """
    Creates a file to register excluded PRs for a given project.

    This method generates a JSON file to store information about PRs that should be excluded
    from SonarQube analysis for the specified project.

    Args:
        repo (str): The name of the repository.

    Returns:
        None
    """
        
    exclude_file_path = f"./3-SonarQube_Execution/logs/exclude_prs_{repo}.json"

    if (os.path.exists(exclude_file_path)):
        return
    
    write_output_file(exclude_file_path, {})

def add_pr_to_exclude_prs(repo: str, pr_number: int, reason: str) -> None:
    """
    Adds a pull request to the list of excluded PRs for a given project.

    This method adds the specified pull request number along with a reason for exclusion
    to the JSON file that stores information about excluded PRs for the specified project.

    Args:
        repo (str): The name of the repository.
        pr_number (int): The number of the pull request to be excluded.
        reason (str): The reason for excluding the pull request.

    Returns:
        None
    """
        
    exclude_file_path = f"./3-SonarQube_Execution/logs/exclude_prs_{repo}.json"

    excluded_prs = read_input_file(exclude_file_path)

    excluded_prs[pr_number] = reason

    write_output_file(exclude_file_path, excluded_prs)

def check_prs_to_process(repo: str, output_directory: str, exclude_prs_file: str, prs: List[Dict]) -> List[Dict]:
    """
    Filters the pull requests that are eligible for analysis.

    This method checks the pull requests that are available for analysis based on the following criteria:
    1. Pull requests that have not been previously processed.
    2. Pull requests that are not excluded from analysis due to specific reasons.

    Args:
        repo (str): The name of the repository.
        output_directory (str): The directory where output files are stored.
        exclude_prs_file (str): The path to the file containing excluded pull requests.
        prs (List[Dict]): A list of dictionaries containing information about pull requests.

    Returns:
        List[Dict]: A filtered list of pull requests that are eligible for analysis.
    """

    all_prs = {}

    for pr in prs:
        all_prs[pr["pr_number"]] = pr

    for _, _, filenames in os.walk(output_directory):
        current_processed_prs =  set([int(file.removeprefix(f"issues_{repo}_").removesuffix(".json")) for file in filenames if repo in file])

    excluded_prs = read_input_file(exclude_prs_file)
    
    prs_to_process = [all_prs[pr_number] for pr_number in all_prs.keys() if pr_number not in current_processed_prs and str(pr_number) not in excluded_prs.keys()]

    return prs_to_process

def set_first_commit(commits: List[Dict], start_commit_sha: str, is_pr_commit_first: bool) -> List[Dict]:
    """
    Sets the first commit to be analyzed in the list of commits based on a given start commit SHA.

    This method adjusts the order of commits in a list based on whether the start commit SHA
    corresponds to the first commit in the list or not.

    Args:
        commits (List[Dict]): A list of dictionaries containing information about commits.
        start_commit_sha (str): The SHA of the start commit.
        is_pr_commit_first (bool): Indicates whether the start commit is the first commit in the list.

    Returns:
        List[Dict]: The list of commits with the first commit adjusted as specified.
    """

    if is_pr_commit_first:
        commits.insert(0, start_commit_sha)
    else:
        start_commit_index = [i for i, commit in enumerate(commits) if commit == start_commit_sha][0]
        commits = commits[start_commit_index:]

    return commits

def download_commit(project_url: str, commit_sha: str) -> None:
    """
    Downloads the code corresponding to a given commit SHA and extracts it.

    This method downloads the code associated with a specific commit SHA from the project's URL
    and then extracts the downloaded ZIP file to the current directory.

    Args:
        project_url (str): The URL of the project repository.
        commit_sha (str): The SHA of the commit to be downloaded.

    Returns:
        None
    """

    commit_url = f"{project_url}/archive/{commit_sha}.zip"

    response = requests.get(commit_url, stream=True)

    zip = zipfile.ZipFile(io.BytesIO(response.content))
    zip.extractall()

def delete_code_directory(repo: str, commit_sha: str) -> None:
    """
    Deletes the directory containing code associated with a specific commit.

    This method removes the directory containing the code related to a specific commit
    from the file system.

    Args:
        repo (str): The name of the repository.
        commit_sha (str): The SHA of the commit whose directory should be deleted.

    Returns:
        None
    """
        
    shutil.rmtree(f"./{repo}-{commit_sha}")

def get_build_command_for_repo(repo: str) -> str:
    """
    Retrieves the build command for a repository.

    Args:
        repo (str): Name of the repository.

    Returns:
        str: Build command for the repository.

    Raises:
        Exception: If the repository does not have a build command in the build commands file.
    """

    build_commands = read_input_file(BUILD_COMMANDS_FILE)

    if repo not in build_commands:
        raise Exception(f"{repo} has not build command in build commands file!")

    return build_commands[REPO]

REPO = "helix"
PROJECT_URL = f"https://www.github.com/apache/{REPO}"
EXCLUDE_PRS_FILE = f"./3-SonarQube_Execution/logs/exclude_prs_{REPO}.json"
INPUT_DIRECTORY = "./2-PRs_Processing/2.5-Identify_Start_Commit/Output"
OUTPUT_DIRECTORY = "./3-SonarQube_Execution/Output"
BUILD_COMMANDS_FILE = "./3-SonarQube_Execution/build_commands.json"

create_exclude_prs_file(REPO)

prs = read_input_file(f"{INPUT_DIRECTORY}/{REPO}.json")
prs = check_prs_to_process(REPO, OUTPUT_DIRECTORY, EXCLUDE_PRS_FILE, prs)

logger = setup_logger()
sonar_api = SonarQubeApi(True)
metrics_collector = SonarMetricsCollector(sonar_api)
execution_monitor = ExecutionMonitor(REPO)
build_handler = BuildHandler(get_build_command_for_repo(REPO))
sonarqube_runner = SonarQubeRunner()

for i in range(len(prs)):
    pr_number = prs[i]["pr_number"]
        
    sonar_project = f"{REPO}-{pr_number}"

    try:
        logger.debug(f"Starting PR {pr_number}")

        execution_monitor.start_monitoring()

        logger.debug(f"Creating sonar project: {sonar_project}...")
        sonar_api.create_project(sonar_project, sonar_project)

        changed_files = prs[i]["changed_files"]

        issues_json = f"{OUTPUT_DIRECTORY}/issues_{REPO}_{pr_number}.json"
        issues = []

        commits = [commit["sha"] for commit in prs[i]["commits"]]
        start_commit = prs[i]["start_commit"]
        is_pr_commit_first = prs[i]["is_pr_commit_first"]
        
        logger.debug(f"Setting first commit...")
        commits = set_first_commit(commits, start_commit, is_pr_commit_first)

        commits_length = len(commits)
        logger.debug(f"Total commits: {commits_length}")

        for j in range(commits_length):
            commit_sha = commits[j]
            logger.debug(f"Starting to process commit {j+1} of {commits_length} [{commit_sha}]")
            execution_monitor.start_commit_monitoring()

            logger.debug("Downloading commit...")
            download_commit(PROJECT_URL, commit_sha)

            logger.debug("Checking build files...")
            build_handler.check_build_files(REPO, pr_number, commit_sha)

            logger.debug("Compiling...")
            is_compile_success = build_handler.compile_project(REPO, pr_number, commit_sha)

            if not is_compile_success:
                delete_code_directory(REPO, commit_sha)
                error_msg = f"Failed to compile... PR: {pr_number}, commit: {commit_sha}"
                add_pr_to_exclude_prs(REPO, pr_number, error_msg)
                raise Exception(error_msg)

            logger.debug("Running sonar analysis...")
            is_analysis_success = sonarqube_runner.run_analysis(REPO, pr_number, commit_sha, sonar_project, sonar_project)

            if not is_analysis_success:
                delete_code_directory(REPO, commit_sha)
                error_msg = f"Failed to run sonar... PR: {pr_number}, commit: {commit_sha}"
                add_pr_to_exclude_prs(REPO, pr_number, error_msg)
                raise Exception(error_msg)

            current_analysis = j + 1

            logger.debug("Waiting for analysis to be available for collect...")
            while True:
                total_analyses = sonar_api.get_project_total_analyses(sonar_project)
                total_analyses_by_activity = sonar_api.get_total_analyses_by_ce_activity(sonar_project)

                is_analysis_available = (
                    total_analyses == current_analysis and 
                    total_analyses_by_activity == current_analysis
                )

                if is_analysis_available:
                    logger.debug("Analysis available... Collecting issues...")
                    break
                else:
                    time.sleep(1)

            logger.debug("Collecting metrics...")
            metrics = metrics_collector.get_metrics(sonar_project, changed_files, prs[i]["moved_files"])

            issues.append({
                "commit_sha": commit_sha,
                "issues": sonar_api.get_issues_for_files(sonar_project, changed_files),
                "metrics": metrics
            })
            delete_code_directory(REPO, commit_sha)

            execution_monitor.end_commit_monitoring(commit_sha)
            logger.debug(f"Execution for PR {pr_number} commit {j+1} ended")

        logger.debug("All commits processed")
        logger.debug("Saving issues data...")
        write_output_file(issues_json, issues)

        execution_monitor.end_monitoring(pr_number)
        logger.debug(f"PR {pr_number} was successfully processed!")

    except Exception as error:
        sonar_api.delete_project(sonar_project)
        logger.debug('\033[91m' + str(error) + '\033[0m')
        traceback.print_exc()