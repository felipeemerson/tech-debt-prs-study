import os
from datetime import datetime
from commons.IOUtils import write_output_file

class DataProcessor:
    @staticmethod
    def process_files(input_directory: str, output_directory: str, process_function: callable) -> None:
        """
        Processes files within a directory using a custom process function.
        If the repo has already been processed, then it will be skipped.

        Args:
            input_directory (str): The path to the directory containing input files.
            output_directory (str): The path to the directory where output files will be written.
            process_function (callable): A function that takes a file path as input and processes it.
        """
        start = datetime.now()
        print(f"Starting to process... Init time: {start}")

        for dirpath, _, filenames in os.walk(input_directory):
            for file in filenames:
                input_file_path = os.path.join(dirpath, file)
                repo = file.removesuffix(".json")
                output_file_path = os.path.join(output_directory, f"{repo}.json")

                if os.path.exists(output_file_path):
                    print(f"The repo {repo} has already been processed! Skipping...")
                    continue

                print(f"Starting to process {repo} PRs")

                processed_data = process_function(input_file_path)

                write_output_file(output_file_path, processed_data)

        end = datetime.now()
        print(f"All PRs processed successfully! Time tooked: {end - start}")