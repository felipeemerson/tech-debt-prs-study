# Data collection and processing

This directory contains all scripts related to downloading PRs, processing them, running them with SonarQube, and preparing them for analysis. All the code was written in [Python](https://www.python.org/), specifically tested on version 3.10.11. To execute the scripts, consider this directory (`Step_1_to_4`) as the root directory.

## Setup

Before running any script, Python must be installed. The next step is installing dependencies. To do this, open a terminal and execute the following commands:

```bash
# Install required dependencies
$ pip install -r requirements.txt

# Setup this project
$ pip install -e .
```

Additionally, it's important to set up three environment variables. Configuration can be done in a file `./.env`. The variables are:


- **GITHUB_TOKEN**: token for authentication in calls to the GitHub API;
- **SONAR_TOKEN**: token for authentication in calls to the SonarQube API;
- **SONAR_HOST**: host of the SonarQube instance.

## Step 1 - PRs Mining

PR mining is performed in the directory `./1-PRs_Mining/` by running the script `./1-PRs_Mining/mining_prs.py`. Before running it, it's important to configure from which projects PRs will be mined. This can be done in the file `./1-PRs_Mining/Input/repos.json`. The mined PRs are stored in the directory `./1-PRs_Mining/Output/`. Each project will have a JSON file with its mined PRs in the format **repo_name.json**, where **repo_name** is the project name.

## Step 2 - PRs Processing

The directory for PR processing is `./2-PRs_Processing/`.

### Step 2.1 - Filter by merged date

In this stage, PRs are filtered by merge date, keeping only those whose merge date is up to February 29, 2024, at 23:59:59. To execute this stage, simply run the script `./2-PRs_Processing/2.1-Filter_PRs_by_Merged_Date/filter_by_merged_date.py`. The filtered PRs will be stored in `./2-PRs_Processing/2.1-Filter_PRs_by_Merged_Date/Output`.

### Step 2.2 - Identify PR commit

The PR commit is the last commit before the PR initiation. In this step, the PR commit is identified and stored in the key **pr_commit** in the object of each PR. To execute this stage, simply run the script `./2-PRs_Processing/2.2-Identify_PR_Commit/identify_pr_commit.py`. The result is stored in `./2-PRs_Processing/2.2-Identify_PR_Commit/Output`.

### Step 2.3 - Filter PRs with pulls

As PR with code pulled from other branches may contain new TD or fixed pre-existing TD, we remove PRs with pulls that occurred in the middle of commits. If the PR has only one pull and it's in the last commit, we keep the PR but reduce the commit range to the penultimate commit. To execute this step, simply run the script `./2-PRs_Processing/2.3-Filter_PRs_with_Pulls/filter_pulls.py`. The result is stored in `./2-PRs_Processing/2.3-Filter_PRs_with_Pulls/Output`.

### Step 2.4 - Check changed files

As indicated in the study, we narrow down the scope of the analyzed project to only the files involved in the PR. This step aims to identify these files, recognize moved files (storing both the old and new paths), and filter out PRs that do not alter Java files, the language we focus on. To execute this step, simply run the script `./2-PRs_Processing/2.4-Check_Changed_Files/check_changed_files.py`. The result is stored in `./2-PRs_Processing/2.4-Check_Changed_Files/Output`.

### Step 2.5 - Identify start commit

The identification of pre-existing issues is done at the commit preceding the PR commit, as anything after it would have been added during the PR. We identify the "preceding commit" using two strategies: (i) in cases where there is a commit before the PR commit within the branch, the preceding commit is the last commit before the PR commit; (ii) in cases where there is no commit before the PR commit within the branch, we use the concept of parent commit and consider the parent of the PR commit as the preceding commit. To execute this step, simply run the script `./2-PRs_Processing/2.5-Identify_Start_Commit/identify_start_commit.py`. The result is stored in `./2-PRs_Processing/2.5-Identify_Start_Commit/Output`.

## Step 3 - SonarQube Execution

In step 3, each PR is analyzed through SonarQube. As indicated in the study, we use SonarQube version 10.0.0.68432 along with SonarScanner CLI version 4.8.0.2856. To facilitate the setup of the environment that we use, we have created an Ansible playbook (`../SonarQube_Environment_Setup/environment_setup.yaml`) that allows configuring the environment on an Ubuntu machine (preferably Ubuntu 22.04.1 LTS). This configuration is explained in the README file in the directory `../SonarQube_Environment_Setup`.

The execution of this step is done through the script `./3-SonarQube_Execution/run_sonar_analysis.py`. Before running it, it's important to set the variable **REPO** with the name of the project to be executed. Additionally, add the build command of the project in the `./3-SonarQube_Execution/build_commands.json` file. Furthermore, if you wish to execute only a subset of PRs from a project, you can create a filter at the beginning of the execution based on the **pr_number** of the PR.

To streamline executions, we have created a file to exclude PRs for each project located in the directory `./3-SonarQube_Execution/logs/`, following the format `exclude_prs_repo.json`, where **repo** is the name of the project. This allows PRs that fail compilation or SonarQube execution to be excluded, facilitating the resumption of executions after the script is stopped. Similarly, at the beginning, the script checks which PRs have already been processed and skips them.


Additionally, in this step, we perform monitoring of the duration of each commit of each PR and store this information in the directory `./3-SonarQube_Execution/logs/monitoring`. We also record various logs: execution logs (`./3-SonarQube_Execution/logs/executions.log`), build error logs (`./3-SonarQube_Execution/logs/build-errors.log`), and SonarQube execution error logs (`./3-SonarQube_Execution/logs/sonar-execution-errors.log`).


The issues identified in each PR are stored in the directory `./3-SonarQube_Execution/Output/`, in the format `issues_repo_pr-number.json`, where **repo** is the project name and **pr-number** is the PR number.

## Step 4 - Post-processing

The post-processing directory is `./4-Post_Processing/`.

### Step 4.1 - Issues Processing

The processing of issues is performed in the script `./4-Post_Processing/4.1-Issues_Processing/process_issues.py`, and as a result, we have the dataset of issues located at `./4-Post_Processing/4.1-Issues_Processing/Output`.

In the processing of issues, we classified them by origin and status.

### Step 4.2 - Monitoring Processing

The monitoring dataset is generated by the script `./4-Post_Processing/4.2-Monitoring_Processing/monitoring_processing.py` and stored in `./4-Post_Processing/4.2-Monitoring_Processing/Output`.

### Step 4.3 - PRs Characterization Processing

Finally, the dataset for PR characterization is generated by the script `./4-Post_Processing/4.3-PRs_Characterization_Processing/monitoring_processing.py` and stored in `./4-Post_Processing/4.3-PRs_Characterization_Processing/Output`. We only consider the 2,035 PRs that successfully ran SonarQube.

## Extra

The `./Extra` directory have some utility scripts.