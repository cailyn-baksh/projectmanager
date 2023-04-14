#!/usr/bin/env python3

import argparse
import configparser
import io
import os
import os.path
import random
import subprocess
import sys
import time

import updater

VERSION = "0.1.0"

class Tee(io.TextIOBase):
    """
    Tees an output stream into two different streams. Both streams must have a
    write(string) method
    """
    def __init__(self, file1: io.IOBase, file2: io.IOBase):
        self.file1 = file1
        self.file2 = file2

    def write(self, s):
        self.file1.write(s)
        self.file2.write(s)


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
        """
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
        project = random.choice([proj for proj in self.config.sections() if proj not in self.RESERVED_CONFIG_NAMES])

        print(f"{project}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="ProgramManager",
                                     description="Helps manage your projects")

    parser.add_argument("--version", action="version", version=f"%(prog)s v{VERSION}")
    parser.add_argument("--config", metavar="PATH", default="~/.config/.pm", help="Set the config directory.")

    parser_history_grp = parser.add_argument_group("History")
    parser_history_grp.add_argument("--clear-history", action="store_true", help="Clear the program's history")

    subparsers = parser.add_subparsers(dest="cmd", title="Commands", help="Run --help on each subcommand for specific usage information")

    parser_update_cmd = subparsers.add_parser("update", help="Check for and install updates")

    parser_list_cmd = subparsers.add_parser("list", help="List all the registered project")

    parser_add_cmd = subparsers.add_parser("add", help="Add a project")
    parser_add_cmd.add_argument("name", help="The name of the project. This name must be unique.")
    parser_add_cmd.add_argument("path", help="The path to the project.")

    parser_rand_cmd = subparsers.add_parser("random", help="Pick a random project")

    parser_set_cmd = subparsers.add_parser("set", help="Set a value")
    parser_set_cmd.add_argument("project", help="The project to set the value for")
    parser_set_cmd.add_argument("property", choices=["active", "inactive"], help="The property value to set for the given project")

    args = parser.parse_args()

    with ProjectManager(args.config) as pm:
        if args.cmd == "update":
            updater.update()
        elif args.cmd == "list":
            pm.list_projects()
        elif args.cmd == "add":
            pm.add_project(args.name, args.path)
        elif args.cmd == "random":
            pm.random_project()
