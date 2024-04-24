import os
import pandas as pd
from commons.IOUtils import read_input_file

MONITORING_DIRECTORY = "./3-SonarQube_Execution/logs/monitoring"
OUTPUT_DIRECTORY = "./4-Post_Processing/4.2-Monitoring_Processing/Output"

processed_prs = []

for dirpath, dirnames, filenames in os.walk(MONITORING_DIRECTORY):
  prs = {}

  for file in filenames:
    monitoring_data = read_input_file(f"{MONITORING_DIRECTORY}/{file}")

    repo = file.removesuffix(".json")
    
    for pr_number in monitoring_data:
        print(f"processing repo {repo} pr {pr_number}")

        current_pr = monitoring_data[pr_number]

        for commit in current_pr:
            processed_prs.append({
                "pr_number": pr_number,
                "repo": repo,
                "commit": commit,
                "duration": current_pr[commit]
            })

df = pd.DataFrame(processed_prs)
df.to_csv(f"{OUTPUT_DIRECTORY}/prs_monitoring.csv", header=True, index=False)