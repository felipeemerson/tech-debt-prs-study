import os
from commons.DataProcessor import DataProcessor
from commons.IOUtils import read_input_file

def check_prs_size_by_file(file: str, repo: str) -> None:
    """
    Checks the number of PRs of a repo and prints the result.

    Args:
        file (str): Path to the file containing PRs.
        repo (str): Name of the repository.

    Returns:
        None
    """

    prs = read_input_file(file)

    print(f"Repo {repo} has {len(prs)} PRs")

def check_prs_by_directory(directory: str) -> None:
    """
    Checks the number of PRs for each repo within a directory and prints the results.

    Args:
        directory (str): Path to the directory containing files with PRs.

    Returns:
        None
    """
    for dirpath, _, filenames in os.walk(directory):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            repo = file.removesuffix(".json")

            check_prs_size_by_file(file_path, repo)
    
def check_prs_issues() -> None:
    """
    Checks the number of PRs that ran SonarQube successfully and prints the results.

    Returns:
        None
    """
    for dirpath, _, filenames in os.walk("3-SonarQube_Execution/Output"):
        repos_count = {}

        for file in filenames:
            repo = file.removesuffix(".json").split("_")[1]

            repos_count[repo] =  repos_count[repo] + 1 if repo in repos_count else 1
        
        for k, v in repos_count.items():
            print(f"Repo {k} has {v} PRs")



directories = [
    "2-PRs_Processing/2.1-Filter_PRs_by_Merged_Date/Output",
    "2-PRs_Processing/2.5-Identify_Start_Commit/Output"
]

print(f"#### 1 - mined PRs (Step 1) ####")
check_prs_by_directory(directories[0])

print(f"\n#### 2 - Processing (Step 2.5) ####")
check_prs_by_directory(directories[1])

print(f"\n#### 3 - Post-execution (Step 3) ####")
check_prs_issues()