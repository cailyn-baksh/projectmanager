"""
Module which checks for and installs updates for the project manager
"""

import subprocess

REPO_URL = "http://github.com/cailyn-baksh/projectmanager.git"

"""
git fetch origin
BRANCH = git rev-parse --abbrev-ref HEAD
print(f"Checking for updates on branch {BRANCH})

LOCAL = git log -n 1 --pretty=format:'%H' {BRANCH}"
REMOTE = git log -n 1 --pretty=format:'%H' origin/{BRANCH}"

if LOCAL != REMOTE:
    # Update
    git pull {REPO_URL}
"""


def run_and_log(cmd, *args, **kwargs):
    print(f" : {cmd}")

    return subprocess.run(cmd.split(' '), *args, **kwargs)


def update(check_only=False, confirm=True):
    """
    Checks for and installs updates

    check_only  If true, check for updates and then exit.
    confirm     If true, confirm before installing updates.
    """

    print("Checking for updates...")

    # Fetch remote changes
    run_and_log(
        f"git fetch {REPO_URL}",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )

    # Get the current branch name
    branch = run_and_log(
        "git rev-parse --abbrev-ref HEAD",
        capture_output=True
    ).stdout.decode("utf-8").rstrip()

    # Get the latest local & remote hashes
    local_hash = run_and_log(
        f"git log -n 1 --pretty=format:'%H' {branch}",
        capture_output=True
    ).stdout.decode("utf-8").rstrip()
    remote_hash = run_and_log(
        f"git log -n 1 --pretty=format:'%H' origin/{branch}",
        capture_output=True
    ).stdout.decode("utf-8").rstrip()

    if local_hash != remote_hash:
        print("Updates are available!", end=' ')

        if check_only:
            return

        choice = input("Do you want to install them? [Y/n] ") \
            if confirm else 'Y'

        if choice.upper() != 'N':
            print("Installing Updates...")

            run_and_log(f"git pull {REPO_URL}")

            print("Updates have been installed")
        else:
            print("Cancelling update.")
    else:
        print("Already up-to-date!")


if __name__ == "__main__":
    print("Run 'pm update' to check for & install updates")
    exit(1)

