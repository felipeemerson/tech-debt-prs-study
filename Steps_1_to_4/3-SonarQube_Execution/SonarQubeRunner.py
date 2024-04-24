import subprocess
import os
import logging
from dotenv import load_dotenv
from typing import List

class SonarQubeRunner:
    """
    A class for executing SonarQube analysis on a given project. 
    Any errors that occur during the analysis are logged to a file.

    Attributes:
        __token (str): The SonarQube authentication token, retrieved from the environment.
        host (str): The SonarQube server host URL, retrieved from the environment.
        __log_file (str): The path to the SonarQube execution errors log file.
        __logger (logging.Logger): The logger object for logging execution errors.
    """

    def __init__(self) -> None:
        """
        Initializes the SonarQubeRunner object.
        """

        load_dotenv()
        self.__token = os.getenv("SONAR_TOKEN")
        self.host = os.getenv("SONAR_HOST")
        self.__log_file = "./3-SonarQube_Execution/logs/sonar-execution-errors.log"
        self.__logger = self.__setup_logger()

    def __setup_logger(self) -> logging.Logger:
        """
        Sets up the logger for logging SonarQube execution errors.

        Returns:
            logging.Logger: The logger object for logging SonarQube execution errors.
        """
                
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.ERROR)
        
        file_handler = logging.FileHandler(self.__log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger

    @staticmethod
    def extract_sonar_error_message_lines(error_lines: List[str]) -> List[str]:
        """
        Extracts Sonar-Scanner error message lines from the output.

        Args:
            error_lines (List[str]): List of lines from the error output.

        Returns:
            List[str]: List of Sonar-Scanner error message lines.
        """
                
        match = "------------------------------------------------------------------------"

        # Finds the index where the error message starts
        start_index = -1
        for line in error_lines[::-1]:
            if match in line:
                break
                
            start_index -= 1

        return error_lines[start_index-10:start_index]

    
    def run_analysis(self, repo: str, pr_number: int, commit_sha: str, projectKey: str, projectName: str) -> bool:
        """
        Executes SonarQube analysis on the specified project using Sonar Scanner.

        Args:
            repo (str): The name of the repository.
            pr_number (int): The number of the pull request.
            commit_sha (str): The SHA of the commit.
            projectKey (str): The key of the project in SonarQube.
            projectName (str): The name of the project in SonarQube.

        Returns:
            bool: True if the analysis is successful, False otherwise.
        """
                
        sonar_scanner_command = f"sonar-scanner -Dsonar.token={self.__token}  \
            -Dsonar.projectKey={projectKey} \
            -Dsonar.projectName='{projectName}' \
            -Dsonar.projectBaseDir='.' \
            -Dsonar.host.url={self.host} \
            -Dsonar.scm.disabled=true \
            -Dsonar.language=java \
            -Dsonar.java.binaries=**/target/classes \
            -Dsonar.exclusions=**/*.py,**/*.css,**/*.js,**/*.ts,**/*.jsx,**/*.tsx,**/*.xml,,**/*.yaml,**/*.html"
        
        try:
            subprocess.run(
                f"cd {repo}-{commit_sha} && {sonar_scanner_command}",
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )

            return True

        except subprocess.CalledProcessError as err:
            error_lines = err.output.splitlines()

            error_message_lines = self.extract_sonar_error_message_lines(error_lines)
            self.__logger.error(f"Error to execute sonar in commit {commit_sha} of PR {pr_number} of repo {repo}")
            self.__logger.error('\n' + '\n'.join(error_message_lines) + '\n')
            return False
