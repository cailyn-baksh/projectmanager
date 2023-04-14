"""
Module which checks for and installs updates for the project manager
"""

import subprocess

def update():
    """
    Checks for and installs updates
    """
    UPDATE_CHECK_CMD = "git log -n 1 --pretty=format:'%H'".split(' ')
    UPDATE_CHECKOUT_CMD = "git checkout main".split(' ')
    UPDATE_INSTALL_CMD = "git pull".split(' ')

    # TODO: add support for alternate branches
    current_hash = subprocess.run(
            UPDATE_CHECK_CMD + ["main"],
            capture_output=True
        ).stdout
    remote_hash = subprocess.run(
            UPDATE_CHECK_CMD + ["origin/main"],
            capture_output=True
        ).stdout

    if current_hash != remote_hash:
        choice = input("Updates are available! Do you want to install them? [Y/n] ")

        if choice.upper() != 'N':
            # Install updates

            subprocess.run(UPDATE_CHECKOUT_CMD)
            subprocess.run(UPDATE_INSTALL_CMD)

            print("Done!")
        else:
            print("Cancelling update.")
    else:
        print("Already up-to-date!")


if __name__ == "__main__":
    print("Run 'pm update' to check for & install updates")
    exit(1)

