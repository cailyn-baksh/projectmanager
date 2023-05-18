#!/usr/bin/env python3

import argparse
import inspect
import io

import manager
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


class CLI(argparse.ArgumentParser):
    """
    CLI based on argparse.ArgumentParser.

    Usage: Instantiate the cli, then define functions to handle parsing the
    arguments using the decorators provided by this class.

    Examples:
    """
    subparsers = None

    def __init__(self, **kwargs):
        """See argparse.ArgumentParser.__init__"""
        super().__init__(**kwargs)

    def subcommand(self, args=[]):
        """
        Create a subcommand along with a function to parse the args.

        The function should be named the same as the subcommand's name,
        prefixed with `subcmd_`. If this is not the case, then the function's
        full name is used as teh subcommand name.

        The subcommand will use the function's docstring as the help string.
        The first line will be shown in the general --help option, and the
        entire string will be shown in the subcommand's specific --help.
        """

        if self.subparsers is None:
            # Make sure that subparsers has been initialized
            self.subparsers = self.add_subparsers(
                title="Subcommands", dest="cmd",
                help="Use `--help` for specific help information for each"
                " subcommand."
            )

        def decorator(func):
            # Get the docstring for func
            docstring = inspect.getdoc(func) or ""
            short_help = docstring.split('\n')[0]

            # Create the subcommand parser
            parser = self.subparsers.add_parser(
                func.__name__.removeprefix("subcmd_"),
                help=short_help,
                description=docstring
            )

            # Add the subcommand's arguments
            for arg in args:
                parser.add_argument(*arg[0], **arg[1])

            # Apply the parsing function
            parser.set_defaults(func=func)

        return decorator

    @staticmethod
    def argument(*name_or_flags, **kwargs):
        """Construct an arguemnt to pass to @subcommand"""
        return ([*name_or_flags], kwargs)


if __name__ == "__main__":
    # Create CLI
    cli = CLI(prog="ProgramManager",
              description="Helps manage your projects")

    # Basic Args
    cli.add_argument(
        "--version", action="version", version=f"%(prog)s v{VERSION}"
    )
    cli.add_argument(
        "--config", metavar="PATH", default="~/.config/.pm",
        help="Set the config directory."
    )

    # History Args
    cli_history_grp = cli.add_argument_group("History")
    cli_history_grp.add_argument(
        "--clear-history", action="store_true",
        help="Clear the program's history"
    )

    # Subcommands
    @cli.subcommand([
        CLI.argument(
            "-y", action="store_false", dest="confirm_install",
            help="Do not prompt before installing updates"
        )
    ])
    def update(args):
        """Check for and install updates"""
        pass

    # parser_list_cmd = subparsers.add_parser(
    #     "list", help="List all the registered project"
    # )

    # parser_add_cmd = subparsers.add_parser("add", help="Add a project")
    # parser_add_cmd.add_argument(
    #     "name", help="The name of the project. This name must be unique."
    # )
    # parser_add_cmd.add_argument("path", help="The path to the project.")

    # parser_rand_cmd = subparsers.add_parser(
    #     "random", help="Pick a random project"
    # )

    # parser_set_cmd = subparsers.add_parser("set", help="Set a value")
    # parser_set_cmd.add_argument(
    #     "project", help="The project to set the value for"
    # )
    # parser_set_cmd.add_argument(
    #     "property", choices=["active", "inactive"],
    #     help="The property value to set for the given project"
    # )

    # parser_idea_cmd = subparsers.add_parser(
    #     "ideas", help="Store ideas for future projects"
    # )
    # parser_set_cmd.add_argument(
    #     "cmd", default="list", choices=["list", "add", "remove", "show"],
    #     help="The subcommand to run on "
    # )

    #parser_set_cmd.add_argument("list", help="List the project ideas")
    #parser_set_cmd.add_argument("new", help="Add a new idea")
    #parser_set_cmd.add_argument(
    #    "remove", help="Remove an idea from the idea database"
    #)
    #parser_set_cmd.add_argument("show", help="Show a

    args = cli.parse_args()

    with manager.ProjectManager(args.config) as pm:
        if args.cmd == "update":
            updater.update(args.confirm_install)
        elif args.cmd == "list":
            pm.list_projects()
        elif args.cmd == "add":
            pm.add_project(args.name, args.path)
        elif args.cmd == "random":
            pm.random_project()

