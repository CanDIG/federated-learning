#!/usr/bin/env python3

import importlib
import sys
import os
import re

def get_file_string(location: str):
    """
    Function to return the contents of the file at location, as a string
    """

    with open(location, "r") as infile:
        return infile.read()

def remove_mount_folder(identifier, file_string):
    """
    Function to remove a folder that has been bind mounted from the file contents
    """

    matches = re.findall(f'.*/{identifier}/.*\n', file_string)
    for match in matches:
        file_string = file_string.replace(match, '')
    
    return file_string

def remove_mount_file(filename, file_string):
    """
    Function to remove a file that has been bind mounted from the file contents
    """

    matches = re.findall(f'.*/{filename}.*\n', file_string)
    for match in matches:
        file_string = file_string.replace(match, '')
    
    return file_string

def parse_args(arg: str, file_string: str):
    """
    Function to parse the option entered from the command line and to perform the corresponding action.

    -e: Remove the experiment folder as a bind mount
    -b: Remove the bases folder as a bind mount
    -k: Remove the Katsu entrypoint as a bind mount
    -i: Remove the Katsu ingestion scripts as a bind mount
    """

    if arg.strip() == "-e":
        file_string = remove_mount_folder("experiment", file_string)
    elif arg.strip() == "-b":
        file_string = remove_mount_folder("bases", file_string)
    elif arg.strip() == "-k":
        file_string = remove_mount_file("katsu_entrypoint.sh", file_string)
    elif arg.strip() == "-i":
        file_string = remove_mount_folder("ingestion-scripts", file_string)
    
    return file_string

def save_file_here(contents: str, name: str) -> None:
    """
    Function to save a file called `name` in the `pwd` with the given `contents`.

    Can't import from configure_docker_compose.py, because module with dash `orchestration-scripts` cannot be imported from with ease
    """
    
    file = open(name, "w")
    file.write(contents)
    print(f"Modified Docker-Compose File saved at {os.getcwd()}/{name}!")

def main() -> None:
    """
    Function to modify a docker-compose file, given command-line arguments for which bind mounts to remove
    """
    
    args = sys.argv[1:]
    file_string = get_file_string(f"{os.getcwd()}/docker-compose.yml")

    for arg in args:
        file_string = parse_args(arg, file_string)
    
    if "-e" in args and "-b" in args:
        matches = re.findall(r'volumes:\n\s*\n', file_string)
        for match in matches:
            file_string = file_string.replace(match, '\n')
    
    if "-k" in args and "-i" in args:
        matches = re.findall(r'volumes:\n\s*ports', file_string)
        for match in matches:
            file_string = file_string.replace(match, 'ports')

    save_file_here(file_string, "docker-compose.yml")

if __name__ == "__main__":
    main()