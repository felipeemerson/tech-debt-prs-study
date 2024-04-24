import os
import subprocess
import shutil
import re
import logging
from typing import List

class BuildHandler:
    """
    A class for checking and compiling projects. Compilation errors are logged to a file.

    Attributes:
        compile_command (str): The command used to compile the project.
        __log_file (str): The path to the build errors log file.
        __logger (logging.Logger): The logger object for logging build errors.
    """

    def __init__(self, compile_command: str) -> None:
        """
        Initializes the BuildHandler object.

        Args:
            compile_command (str): The command used to compile the project.
        """
                
        self.compile_command = compile_command
        self.__log_file = "./3-SonarQube_Execution/logs/build-errors.log"
        self.__logger = self.__setup_logger()

    def __setup_logger(self) -> logging.Logger:
        """
        Sets up the logger for logging build errors.

        Returns:
            logging.Logger: The logger object for logging build errors.
        """

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.ERROR)
        
        file_handler = logging.FileHandler(self.__log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger

    def check_build_files(self, repo: str, pr_number: int, commit_sha: str) -> None:
        """
        Checks if necessary build files exist for the project.
        Currently, only supports Maven and Gradle build tools.

        Args:
            repo (str): The name of the repository.
            pr_number (int): The number of the pull request.
            commit_sha (str): The SHA of the commit.
        """
                
        pom_location = f"./{repo}-{commit_sha}/pom.xml"
        build_gradle_location = f"./{repo}-{commit_sha}/build.gradle"

        if "mvn" in self.compile_command and not os.path.exists(pom_location):
            shutil.rmtree(f"{repo}-{commit_sha}")
            error_msg = f"Pom file not found for PR: {pr_number}"
            raise Exception(error_msg)
        elif "gradle" in self.compile_command and not os.path.exists(build_gradle_location):
            shutil.rmtree(f"{repo}-{commit_sha}")
            error_msg = f"Gradle file(s) missing for PR: {pr_number}"
            raise Exception(error_msg)

    @staticmethod
    def extract_compile_error_message_lines(error_lines: List[str]) -> List[str]:
        """
        Extracts compilation error message lines from the output.
        Only works with Maven.

        Args:
            error_lines (List[str]): List of lines from the error output.

        Returns:
            List[str]: List of compilation error message lines.
        """
                
        start_lines = [
            "------------------------------------------------------------------------",
            "BUILD FAILURE",
            "------------------------------------------------------------------------"
        ]

        # Finds the index where the error message starts
        start_index = 0
        for i in range(len(error_lines) - 2):
            # It checks if each line is a substring of one of the lines in start_lines
            if all(substring in error_lines[i+j] for j, substring in enumerate(start_lines)):
                start_index = i
                break

        return error_lines[start_index:]

        
    def compile_project(self, repo: str, pr_number: int, commit_sha: str) -> bool:
        """
        Compiles the project and logs any errors.

        Args:
            repo (str): The name of the repository.
            pr_number (int): The number of the pull request.
            commit_sha (str): The SHA of the commit.

        Returns:
            bool: True if compilation is successful, False otherwise.
        """
                
        subprocess.call(f'chmod -R 777 {repo}-{commit_sha}', shell=True)
        try:
            subprocess.run(
                f"cd {repo}-{commit_sha} && {self.compile_command}",
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )

            return True
        except subprocess.CalledProcessError as err:
            error_lines = err.output.splitlines()

            error_message_lines = self.extract_compile_error_message_lines(error_lines)
            self.__logger.error(f"Error to compile commit {commit_sha} of PR {pr_number} of repo {repo}")
            self.__logger.error('\n' + '\n'.join(error_message_lines) + '\n')

            return False
