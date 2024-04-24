from typing import Dict, List
from commons import SonarQubeApi

class SonarMetricsCollector:
    """
    A class for collecting metrics from SonarQube for files in a pull request.
    """

    def __init__(self, sonar_api: SonarQubeApi) -> None:
        """
        Initializes a SonarMetricsCollector instance.

        Args:
            sonar_api (SonarQubeApi): An instance of the SonarQubeApi class for interacting with the SonarQube API.
        """

        self.__sonar_api = sonar_api

    def get_metrics(self, component: str, changed_files: List[str], moved_files: List[Dict]) -> dict:
        """
        Retrieves metrics for a given SonarQube component and adjusts them for moved files in a pull request (PR).

        This method retrieves metrics for a specified SonarQube component and adjusts them to account for moved files
        in a pull request (PR). If a file has been moved, the metrics for the old filepath are set equal to the metrics
        for the new filepath, and vice versa.

        Args:
            component (str): The SonarQube component for which metrics are to be retrieved.
            moved_files (List[Dict]): The list of moved files dicts.
            changed_files (List[str]): The list of modified files in the PR.

        Returns:
            dict: A dictionary containing the adjusted metrics for the specified SonarQube component.
        """
            
        metrics = self.__sonar_api.get_metrics(component)
        changed_files_set = set(changed_files)

        # Removes metrics that are not related with the PR
        for component_file, _ in list(metrics.items()):
            file = component_file.split(":")[1]

            if file not in changed_files_set:
                del metrics[component_file]

        # Sets metrics for old filepath equal to new filepath
        for file in moved_files:
            old_filename = file["old_filename"]
            new_filename = file["new_filename"]
            
            old_component = f"{component}:{old_filename}"
            new_component = f"{component}:{new_filename}"

            if old_component in metrics and new_component not in metrics:
                metrics[new_component] = metrics[old_component]
            
            if new_component in metrics and old_component not in metrics:
                metrics[old_component] = metrics[new_component]

        return metrics
