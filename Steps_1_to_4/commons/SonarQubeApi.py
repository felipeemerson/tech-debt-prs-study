import requests
import os
import logging
from dotenv import load_dotenv
from typing import List, Dict

class SonarQubeApi:
    """
    A class representing an interface to interact with the SonarQube API.

    Attributes:
        base_url (str): The base URL of the SonarQube API.
        with_logging (bool): A flag indicating whether logging is enabled.
        __token (str): The user token for authentication with the SonarQube API, retrieved from the environment.
        __log_file (str): The path to the log file.
        __logger (logging.Logger): The logger object for logging SonarQube API interactions.
    """

    def __init__(self, with_logging: bool) -> None:
        """
        Initializes the SonarQubeApi object by loading the user token from a .env file.

        Args:
            with_logging (bool): A flag indicating whether logging is enabled or not.
        """

        load_dotenv()
        self.__token = os.getenv("SONAR_TOKEN")
        self.base_url = f"{os.getenv('SONAR_HOST')}/api"
        self.__log_file = "./3-SonarQube_Execution/logs/sonarqube.log"
        self.with_logging = with_logging
        self.__logger = self.__setup_logger()
    
    def __setup_logger(self) -> logging.Logger:
        """
        Sets up the logger for the SonarQubeApi object.

        Returns:
            logging.Logger: The logger object configured for logging SonarQube API interactions.
        """

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG if self.with_logging else logging.NOTSET)
        
        file_handler = logging.FileHandler(self.__log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger

    def _make_request(self, method: str, url: str, **kwargs) -> dict:
        """
        Makes a request to the SonarQube API.

        Args:
            method (str): The HTTP method to use for the request (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            url (str): The URL to make the request to.
            **kwargs: Additional keyword arguments to pass to the requests.request() function.

        Returns:
            dict: The response from the SonarQube API.
        """

        headers = {'Authorization': f'Bearer {self.__token}'}
        response = requests.request(method, url, headers=headers, **kwargs)

        return response

    def _make_request_and_get_json(self, method: str, url: str, **kwargs) -> dict:
        """
        Makes a request to the SonarQube API and returns the JSON response.

        Args:
            method (str): The HTTP method to use for the request (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            url (str): The URL to make the request to.
            **kwargs: Additional keyword arguments to pass to the requests.request() function.

        Returns:
            dict: The JSON response from the SonarQube API.

        Raises:
            RuntimeError: If the response status code is not 2xx.
        """
        response = self._make_request(method, url, **kwargs)

        status_code_is_not_2xx = response.status_code // 100 != 2

        if (status_code_is_not_2xx):
            message = f"Error calling SonarQube API. Status Code: {response.status_code}"
            self.__logger.debug(message)
            self.__logger.debug(str(response.content))
            raise RuntimeError(message)

        return response.json()

    def check_project_already_exists(self, component: str) -> bool:
        """
        Checks if a project with the given component key already exists in SonarQube.

        Args:
            component (str): The component key of the project to check.

        Returns:
            bool: True if the project exists, False otherwise.
        """

        endpoint = f"{self.base_url}/components/show"

        querystring = {"component": component}

        response = self._make_request("GET", endpoint, params=querystring)
        
        return response.status_code == 200

    def create_project(self, name: str, project: str) -> None:
        """
        Creates a new project in SonarQube with the given name and project key if it doesn't already exist.

        Args:
            name (str): The name of the project to create.
            project (str): The project key of the project to create.
        """

        if self.check_project_already_exists(project):
            self.__logger.debug("Sonar project already exists")
            return

        endpoint = f"{self.base_url}/projects/create"

        querystring = {
            "name": name,
            "project": project,
        }

        self._make_request_and_get_json("POST", endpoint, params=querystring)

    def create_analysis_token(self, name: str, projectKey: str) -> str:
        """
        Creates an analysis token for the specified project in SonarQube.

        Args:
            name (str): The name of the analysis token.
            projectKey (str): The project key for which the analysis token is created.

        Returns:
            str: The generated analysis token.
        """

        self.__logger.debug(f"Creating analysis token for: {name}")
        endpoint = f"{self.base_url}/user_tokens/generate"

        querystring = {
            "name": name,
            "projectKey": projectKey,
            "type": "PROJECT_ANALYSIS_TOKEN",
        }

        data = self._make_request_and_get_json("POST", endpoint, params=querystring)

        return data["token"]

    def get_project_total_analyses(self, project: str) -> int:
        """
        Retrieves the total number of analyses for a specified project in SonarQube.

        Args:
            project (str): The project key for which to retrieve the total number of analyses.

        Returns:
            int: The total number of analyses for the specified project.
        """

        endpoint = f"{self.base_url}/project_analyses/search"

        querystring = {
            "project": project
        }

        data = self._make_request_and_get_json("GET", endpoint, params=querystring)

        return data["paging"]["total"]

    def get_total_analyses_by_ce_activity(self, project: str) -> int:
        """
        Retrieves the total number of analyses for a specified project in SonarQube, using the /ce/activity endpoint.

        Args:
            project (str): The project key for which to retrieve the total number of analyses.

        Returns:
            int: The total number of analyses for the specified project.
        """
        endpoint = f"{self.base_url}/ce/activity"

        querystring = {
            "component": project
        }

        data = self._make_request_and_get_json("GET", endpoint, params=querystring)

        return data["paging"]["total"]

    def delete_project(self, project: str) -> None:
        """
        Deletes a project from SonarQube.

        Args:
            project (str): The project key of the project to delete.
        """

        endpoint = f"{self.base_url}/projects/delete"

        querystring = {
            "project": project
        }

        self._make_request("POST", endpoint, params=querystring)

    def get_issues(self, component: str, page: int, page_size: int, files: str) -> dict:
        """
        Retrieves issues from SonarQube for a specified component.

        Args:
            component (str): The component key for which to retrieve issues.
            page (int): The page number of the results.
            page_size (int): The number of issues per page.
            files (str): Comma-separated list of files to filter issues by.

        Returns:
            dict: A dictionary containing the JSON of retrieved issues.
        """

        endpoint = f"{self.base_url}/issues/search"

        querystring = {
            "componentKeys": component,
            "languages": "java",
            "p": page,
            "ps": page_size,
            "files": files
        }

        return self._make_request_and_get_json("GET", endpoint, params=querystring)

    def get_issues_for_files(self, component: str, files: List[str]) -> dict:
        """
        Retrieves all issues for each file in a specified component from SonarQube.

        Args:
            component (str): The component key for which to retrieve issues.
            files (List[str]): A list of file paths.

        Returns:
            dict: A dictionary containing all retrieved issues for the specified files.
        """

        issues_fields_to_retrieve = [
            "key",
            "rule",
            "severity",
            "component",
            "status",
            "debt",
            "type",
            "textRange"
        ]

        issues = {
            "issues": [],
            "total": 0
        }

        for file in files:
            page = 1
            page_size = 500

            while True:
                data = self.get_issues(component, page, page_size, file)
                current_issues = data["issues"]

                for issue in current_issues:
                    filtered_issue = {}

                    for field in issues_fields_to_retrieve:
                        if field in issue:
                            filtered_issue[field] = issue[field]

                    issues["issues"].append(filtered_issue)

                total_issues = data["total"]
                issues["total"] += len(current_issues)
                current_number_issues = page * page_size

                self.__logger.debug(f"total issues {total_issues} for file {file}")
                self.__logger.debug(f"current number issues {current_number_issues}")

                page += 1

                all_issues_collected = current_number_issues >= total_issues or page == 20 or total_issues == 0

                if all_issues_collected:
                    break

        return issues

    @staticmethod
    def __get_metric_value(metrics: List[Dict], metric_name: str) -> int:
        """
        Retrieves the value of a specified metric from a list of metrics.

        Args:
            metrics (List[Dict]): A list of dictionaries containing metric information.
            metric_name (str): The name of the metric to retrieve.

        Returns:
            int: The value of the specified metric.
        """

        for metric in metrics:
            if (metric["metric"] == metric_name):
                return metric["value"]

    def __get_metrics(self, project: str, page: int, page_size: int) -> dict:
        """
        Retrieves metrics for a specified project from SonarQube.

        Args:
            project (str): The component key of the project for which to retrieve metrics.
            page (int): The page number of the results.
            page_size (int): The number of metrics per page.

        Returns:
            dict: The JSON response containing the retrieved metrics for the project.
        """
        endpoint = f"{self.base_url}/measures/component_tree"

        querystring = {
            "component": project,
            "metricKeys": "ncloc,complexity",
            "p": page,
            "ps": page_size
        }

        return self._make_request_and_get_json("GET", endpoint, params=querystring)

    def get_metrics(self, project: str) -> dict:
        """
        Retrieves metrics for each class within a specified project from SonarQube.

        Args:
            project (str): The component key of the project for which to retrieve metrics.
            
        Returns:
            dict: A dictionary containing the retrieved metrics for each class in the project.
                The keys are the paths of the classes, and the values are dictionaries with
                'ncloc' and 'complexity' metrics for each class.
        """

        metrics = {}

        current_page = 1
        page_size = 500

        while True:
            data = self.__get_metrics(project, current_page, page_size)

            components = data["components"]

            for component in components:
                component_path = component["key"]
                measures = component["measures"]

                metrics[component_path] = {
                    "ncloc": self.__get_metric_value(measures, "ncloc"),
                    "complexity": self.__get_metric_value(measures, "complexity")
                }

            totalItems = data["paging"]["total"]

            if (totalItems <= current_page * page_size):
                break

            current_page += 1
        return metrics