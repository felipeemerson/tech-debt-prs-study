import os
from typing import List, Dict
from datetime import datetime
from commons.GitHubApi import GitHubGraphQLAPI
from commons.IOUtils import read_input_file, write_output_file

def fetch_pull_requests(owner: str, repo: str) -> List[Dict]:
    """
    Fetches merged pull requests from the specified repository using the GitHub GraphQL API.

    This function initializes a GitHub GraphQL API object with the provided authentication token.
    It then calls the fetch_pull_requests method of the GitHub GraphQL API object to retrieve
    a list of merged pull requests for the given repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.

    Returns:
        List[Dict]: A list of dictionaries representing the fetched merged pull requests.
    """

    gitApi = GitHubGraphQLAPI()

    return gitApi.fetch_pull_requests(owner, repo)

REPOS_FILEPATH = "./1-PRs_Mining/Input/repos.json"
OUTPUT_DIRECTORY = "./1-PRs_Mining/Output"
OWNER = "apache"

repos = read_input_file(REPOS_FILEPATH)

start = datetime.now()

print(f"Starting to collect PRs... Init time: {start}")
for repo in repos:
    output_filepath = f"{OUTPUT_DIRECTORY}/{repo}.json"

    if os.path.exists(output_filepath):
        print(f"The repo {repo} has already been collected! Skipping...")
        continue
    
    print(f"Starting to collect PRs for repo: {repo}")
    pull_requests = fetch_pull_requests(OWNER, repo)

    write_output_file(output_filepath, pull_requests)

    print(f"Collected PRs for repo: {repo}")

end = datetime.now()

print(f"PRs collected... End time: {end}")

print(f"Time tooked: {end - start}")