"""
Module implementing the actual project manager
"""

import configparser
import os
import random


class ProjectManager:
    """
    The main application class
    """

    RESERVED_CONFIG_NAMES = ["DEFAULT", "GLOBAL"]

    def __init__(self, config_dir):
        """
        Construct an instance of the application, using the given config dir
        """
        self.config = configparser.ConfigParser()
        self.config_dir = os.path.abspath(os.path.expanduser(config_dir))

        # Create the config dir if it doesnt exist
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)

        # Load the config file if it exists
        if os.path.isfile(f"{self.config_dir}/config.ini"):
            self.config.read(f"{self.config_dir}/config.ini")

        # Create the global config if it doesnt exist
        if "GLOBAL" not in self.config:
            self.config["GLOBAL"] = {}

    def __enter__(self):
        self.logfile = open(f"{self.config_dir}/output.log", "a+")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(f"{self.config_dir}/config.ini", "w") as f:
            self.config.write(f)

        self.logfile.close()

    def resolve_project(self, name):
        """
        Resolves a project name string into an entry in self.config

        name is the project name string to resolve
        Returns the resolved name, or None if the name does not resolve to
        anything.
        """
        if name == "":
            return None

        if name[0] == '^':
            # Recall history
            # The syntax of this string is ^n where n is a signed integer
            # indicating how many lines back in the output log to search. A
            # positive integer counts backwards from the end of the file, and a
            # negative integer counts forwards from the start of the file.
            # Eg: ^1 refers to the last entry
            # Eg: ^-1 refers to the first entry
            # (if youre whining & shitting your pants about it "not being zero
            # indexed" shut the fuck up dipshit the history log is a circular
            # array it is zero indexed just the 0th index refers to the current
            # entry which has not yet been written and thus cannot be read)

            # Resolve index to recall from history
            history_index = 0

            if len(name) <= 1:
                # just the string ^ resolves to the last entry
                history_index = 1
            else:
                try:
                    history_index = int(name[1:])
                except ValueError:
                    # Invalid string
                    return None

        else:
            if (name in self.config.sections()
                    and name not in self.RESERVED_CONFIG_NAMES):
                return name
            else:
                return None

    def list_projects(self):
        """
        Lists all projects
        """
        # TODO: add paging
        # TODO: add filters
        for key in self.config:
            if key not in self.RESERVED_CONFIG_NAMES:
                print(f"{key}")

    def add_project(self, name, path):
        """doa
        Adds a project to the project database
        """
        if name in self.config:
            # Project already exists
            pass
        else:
            self.config[name] = {
                "path": path,
                "active": True
            }

    def random_project(self):
        project = random.choice([
            proj for proj in self.config.sections()
            if proj not in self.RESERVED_CONFIG_NAMES
        ])

        print(f"{project}")
