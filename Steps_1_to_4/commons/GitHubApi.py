import requests
import os
from time import sleep
from dotenv import load_dotenv
from typing import List, Dict

class _GitHubAPI:
    """
    A class to interact with the GitHub API.

    Attributes:
        None
    """

    def __init__(self) -> None:
        """
        Initializes the GitHubAPI object by loading the personal access token from a .env file.
        """

        load_dotenv()
        self.__token = os.getenv("GITHUB_TOKEN")

    def _make_request(self, method: str, url: str, **kwargs) -> dict:
        """
        Makes a request to the GitHub API.

        Args:
            method (str): The HTTP method to use for the request (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            url (str): The URL to make the request to.
            **kwargs: Additional keyword arguments to pass to the requests.request() function.

        Returns:
            dict: The JSON response from the GitHub API.

        Raises:
            RuntimeError: If the response status code is not 200.
        """

        headers = {'Authorization': f'Bearer {self.__token}'}
        response = requests.request(method, url, headers=headers, **kwargs)

        if (response.status_code != 200):
            message = f"Error calling GitHub API. Status Code: {response.status_code}"
            print(message)
            print(str(response.content))
            raise RuntimeError(message)

        return response.json()

class GitHubGraphQLAPI(_GitHubAPI):
    """
    A class to interact with the GitHub GraphQL API.

    Inherits from GitHubAPI for making requests to the GitHub API.

    Attributes:
        token (str): The personal access token used for authentication.
        base_url (str): The base URL for the GitHub GraphQL API.
    """

    def __init__(self) -> None:
        """
        Initializes the GitHubGraphQLAPI object.

        Args:
            None.
        """

        super().__init__()
        self.base_url = 'https://api.github.com/graphql'

    def execute_query(self, query: str, variables: dict = None) -> dict:
        """
        Executes a GraphQL query against the GitHub GraphQL API.

        Args:
            query (str): The GraphQL query to execute.
            variables (dict, optional): Optional variables to include in the query.

        Returns:
            dict: The JSON response from the GitHub GraphQL API.
        """

        data = {'query': query, 'variables': variables}
        return self._make_request("POST", self.base_url, json=data)

    def fetch_pull_requests(self, owner: str, repo: str) -> List[Dict]:
        """
        Fetches merged pull requests for a specified repository.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.

        Returns:
            List[Dict]: A list of dictionaries containing information about merged pull requests.
        """

        query = """
        query (
            $owner_query: String!
            $repo_query: String!
            $after_var: String
        ) {
            repository(owner: $owner_query, name: $repo_query) {
                pullRequests(
                    first: 100
                    after: $after_var
                    orderBy: { field: CREATED_AT, direction: DESC }
                    states: MERGED
                ) {
                    totalCount
                    edges {
                        node {
                            number
                            createdAt
                            mergedAt
                            additions
					        deletions
					        changedFiles
                            commits(first: 100) {
                                totalCount
                                nodes {
                                    commit {
                                        oid
                                        committer {
                                            date
                                        }
                                        parents (first: 2) {
                                            edges {
                                                node {
                                                    oid
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        """

        after = None
        pull_requests = []

        while True:
            variables = {
                'owner_query': owner,
                'repo_query': repo,
                'after_var': after
            }
            data = self.execute_query(query, variables)

            for edge in data['data']['repository']['pullRequests']['edges']:
                pull_requests.append(edge)

            page_info = data['data']['repository']['pullRequests']['pageInfo']
            has_next_page = page_info['hasNextPage']
            after = page_info['endCursor']

            if has_next_page:
                sleep(120) # sleep 120 seconds before next request
            else:
                break

        return pull_requests

class GitHubRESTAPI(_GitHubAPI):
    """
    A class to interact with the GitHub REST API.

    Inherits from GitHubAPI class.

    Attributes:
        token (str): The personal access token used for authentication.
        base_url (str): The base URL for the GitHub REST API.
    """

    def __init__(self) -> None:
        """
        Initializes the GitHubRESTAPI object.

        Args:
            None
        """

        super().__init__()
        self.base_url = 'https://api.github.com'

    def get_pull_request_changed_files(self, owner: str, repo: str, pr_number: str) -> List[Dict]:
        """
        Retrieves the changed files associated with a pull request from the GitHub REST API.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            pr_number (str): The number of the pull request.

        Returns:
            List[Dict]: A list of dictionaries containing information about each changed file in the pull request.
        """

        method = "GET"
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        files_per_page = 100
        page = 1

        files = []

        while True:
            params = {
                "per_page": files_per_page,
                "page": page
            }

            data = self._make_request(method, url, params=params)

            files.extend(data)
            
            if (len(data) == 0):
                break
        
            page += 1
            sleep(1)

        return files