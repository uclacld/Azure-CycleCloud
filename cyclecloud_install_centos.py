#!/usr/bin/python3
# Prepare an Azure provider account for CycleCloud usage.
import os
import argparse
import json
import re
import random
import platform
from string import ascii_uppercase, ascii_lowercase, digits
import subprocess
from subprocess import CalledProcessError, check_output
from os import path, listdir, chdir, fdopen, remove
from urllib.request import urlopen, Request
from shutil import rmtree, copy2, move
from tempfile import mkstemp, mkdtemp
from time import sleep


tmpdir = mkdtemp()
print("Creating temp directory {} for installing CycleCloud".format(tmpdir))
cycle_root = "/opt/cycle_server"
cs_cmd = cycle_root + "/cycle_server"


def clean_up():
    rmtree(tmpdir)

def _catch_sys_error(cmd_list):
    try:
        output = check_output(cmd_list)
        print(cmd_list)
        print(output)
        return output
    except CalledProcessError as e:
        print("Error with cmd: %s" % e.cmd)
        print("Output: %s" % e.output)
        raise


def install_cc_cli():
    # CLI comes with an install script but that installation is user specific
    # rather than system wide.
    # Downloading and installing pip, then using that to install the CLIs
    # from source.
    if os.path.exists("/usr/local/bin/cyclecloud"):
        print("CycleCloud CLI already installed.")
        return

    print("Unzip and install CLI")
    chdir(tmpdir)
    _catch_sys_error(["unzip", "/opt/cycle_server/tools/cyclecloud-cli.zip"])
    for cli_install_dir in listdir("."):
        if path.isdir(cli_install_dir) and re.match("cyclecloud-cli-installer", cli_install_dir):
            print("Found CLI install DIR %s" % cli_install_dir)
            chdir(cli_install_dir)
            _catch_sys_error(["./install.sh", "--system"])


def already_installed():
    print("Checking for existing Azure CycleCloud install")
    return os.path.exists("/opt/cycle_server/cycle_server")

def download_install_cc():
    print("Installing Azure CycleCloud server")

    _catch_sys_error(["yum", "install", "-y", "cyclecloud8"])

def configure_msft_repos():
    
    configure_msft_yum_repos()


def configure_msft_yum_repos():
    print("Configuring Microsoft yum repository for CycleCloud install")
    _catch_sys_error(
        ["rpm", "--import", "https://packages.microsoft.com/keys/microsoft.asc"])

    with open('/etc/yum.repos.d/cyclecloud.repo', 'w') as f:
        f.write("""\
[cyclecloud]
name=cyclecloud
baseurl=https://packages.microsoft.com/yumrepos/cyclecloud
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
""")

    with open('/etc/yum.repos.d/azure-cli.repo', 'w') as f:
        f.write("""\
[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc      
""")


def install_pre_req():
    print("Installing pre-requisites for CycleCloud server")

    # not strictly needed, but it's useful to have the AZ CLI
    # Taken from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-yum?view=azure-cli-latest

     _catch_sys_error(["yum", "install", "-y", "java-1.8.0-openjdk-headless"])
     _catch_sys_error(["yum", "install", "-y", "azure-cli"])


def main():


    if not already_installed():
        configure_msft_repos()
        install_pre_req()
        download_install_cc()

    install_cc_cli()

    clean_up()


if __name__ == "__main__":
    try:
        main()
    except:
        print("Deployment failed...")
        raise
