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
        Create a subcommand along with a function to parse the args. This
        function takes two arguments, a ProjectManager object, and the
        Namespace returned from ArgumentParser.parse_args().

        The function should be named the same as the subcommand's name,
        prefixed with `subcmd_`. If this is not the case, then the function's
        full name is used as the subcommand name.

        A properly formed function declaration for a subcommand called `foo`
        would look like

        @cli.subcommand(...)
        def subcmd_foo(pm, args):
            ...

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
        ),
        CLI.argument(
            "--check", action="store_true",
            help="Check for updates but don't install"
        )
    ])
    def subcmd_update(pm, args):
        """Check for and install updates"""
        updater.update(args.confirm_install)

    @cli.subcommand()
    def subcmd_list(pm, args):
        """List all the registered projects"""
        pm.list_projects()

    @cli.subcommand([
        CLI.argument(
            "name", help="The name of the project. This name must be unique."
        )
    ])
    def subcmd_add(pm, args):
        """Add a project"""
        pm.add_project(args.name, args.path)

    @cli.subcommand()
    def subcmd_random(pm, args):
        """Pick a random project"""
        pm.random_project()

    @cli.subcommand([
        CLI.argument(
            "project", help="The project to set the property for"
        ),
        CLI.argument(
            "property", help="The property value to set for the given project"
        )
    ])
    def subcmd_set(pm, args):
        """Set a property"""
        pass

    @cli.subcommand([
        CLI.argument(
            "ideacmd", metavar="CMD", default="list",
            choices=["list", "add", "remove", "show"],
            help="The idea subcommand to run"
        )
    ])
    def subcmd_ideas(pm, args):
        """Store ideas for future projects"""
        match args.ideacmd:
            case "list":
                pass
            case "add":
                pass
            case "remove":
                pass
            case "show":
                pass
            case _:
                # Not a valid command; raise error
                pass

    args = cli.parse_args()

    with manager.ProjectManager(args.config) as pm:
        args.func(pm, args)

