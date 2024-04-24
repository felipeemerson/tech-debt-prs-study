# SonarQube environment setup

For SonarQube execution, we created and configured virtual machines using [Oracle VM VirtualBox](https://www.virtualbox.org/) (version 7.0.4 r154605). To streamline the environment setup, we developed an [Ansible](https://www.ansible.com/) playbook that automatically installs and configures the VM. The playbook is named `sonarqube_env_setup.yaml`.

The playbook will automatically install and configure the following software:
- Java JDK 17;
- Maven;
- PostgreSQL (dedicated DB for SonarQube);
- SonarQube;
- SonarScanner CLI.

By default, it will install the versions of SonarQube and SonarScanner used in the paper, but you can change the versions by editing the variables **sonarqube_version** and **sonar_scanner_version**. You can also set a password for the SonarQube database in the **db_password** variable. For projects using other build tools, you can follow the same template and add a task to install them.

## Step-by-step guide to run the playbook

```bash
# Add the Ansible repository to the list of package sources
$ sudo apt-add-repository ppa:ansible/ansible

# Update the package index to ensure it contains the latest packages
$ sudo apt update

# Install Ansible
$ sudo apt install -y ansible

# Copy the content below to this file and save it
$ sudo nano /etc/ansible/hosts

# Create the playbooks directory
$ sudo mkdir /etc/ansible/playbooks/

# Copy the content of the sonarqube_env_setup.yaml playbook to this file or move it to this directory
$ sudo nano /etc/ansible/playbooks/sonarqube_env_setup.yaml

# Run the playbook
$ sudo ansible-playbook /etc/ansible/playbooks/sonarqube_env_setup.yaml

# Restart for the environment variables to be loaded
$ sudo shutdown -r now
```

The content of the file /etc/ansible/hosts:
```
[servers]
localhost ansible_connection=local

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```