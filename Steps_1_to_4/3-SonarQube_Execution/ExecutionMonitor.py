import os
from datetime import datetime
from commons.IOUtils import read_input_file, write_output_file

class ExecutionMonitor:
    """
    A class for monitoring the execution of each commit of each pull request (PR).

    Attributes:
        repo (str): The name of the repository being monitored.
        file (str): The path to the monitoring data file.
        __current_monitoring_data (dict): Dictionary to store current monitoring data.
    """

    def __init__(self, repo: str) -> None:
        """
        Initializes the ExecutionMonitor object.

        Args:
            repo (str): The name of the repository being monitored.
        """
        self.repo = repo
        self.file = f"./3-SonarQube_Execution/logs/monitoring/{self.repo}.json"
        self.__current_monitoring_data = {}

        file_exists = os.path.exists(self.file)
        
        if file_exists:
            return

        write_output_file(self.file, {})

    def start_monitoring(self) -> None:
        """Starts the monitoring process."""

        self.__current_monitoring_data = {}

    def end_monitoring(self, pr_number: int) -> None:
        """
        Ends the monitoring process for a specific pull request (PR).

        Args:
            pr_number (int): The number of the pull request being monitored.
        """

        monitoring = read_input_file(self.file)

        monitoring[pr_number] = self.__current_monitoring_data

        write_output_file(self.file, monitoring)

    def start_commit_monitoring(self) -> None:
        """Starts monitoring the execution of a commit."""

        self.__start_time = datetime.now()

    def end_commit_monitoring(self, commit_sha: str) -> None:
        """
        Ends monitoring the execution of a commit and records the duration.

        Args:
            commit_sha (str): The SHA of the commit being monitored.
        """
        
        end_time = datetime.now()
        self.__current_monitoring_data[commit_sha] = str(end_time - self.__start_time)