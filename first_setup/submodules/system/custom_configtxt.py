import json
import os
import subprocess

class ConfigManager:
    def __init__(self, config_file, json_file):
        self.config_file = config_file
        self.json_file = json_file

    def backup_config(self):
        backup_file = self.config_file + ".bak"
        os.system(f"sudo cp {self.config_file} {backup_file}")
        print(f"Backup of config.txt created at {backup_file}")

    def load_modifications(self):
        with open(self.json_file, 'r') as file:
            modifications = json.load(file)
        return modifications

    def apply_modifications(self, group_name):
        modifications = self.load_modifications()

        if group_name not in modifications:
            print(f"No modification group named '{group_name}' found.")
            return

        group = modifications[group_name]
        self.backup_config()

        # Append modifications to the config.txt
        with open(self.config_file, 'a') as file:
            for line in group['config_lines']:
                file.write(line + "\n")
            print(f"Applied modifications from group '{group_name}' to config.txt")

        # Run any additional commands if specified
        if 'commands' in group:
            for command in group['commands']:
                subprocess.run(command, shell=True)
                print(f"Executed command: {command}")

    def prompt_user_and_apply(self):
        modifications = self.load_modifications()
        print("Available modification groups:")
        for group_name in modifications.keys():
            print(f" - {group_name}")

        group_name = input("Enter the name of the modification group to apply: ")
        self.apply_modifications(group_name)

