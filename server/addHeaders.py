# Generative AI was used during the creation of this file

import os
import subprocess
from datetime import datetime

# Dictionary mapping GitLab handles to full names
GITLAB_USERNAMES = {
    "Teo Portase": "Teo Portase",
    "Michael Koenig": "Michael Koenig",
    "parisab": "Parisa Babaei",
    "schonda": "David Schoen",
    "serbina": "Sofia Serbina",
    "faundez": "Adam Faundez Laurokari"
}

def get_contributors(file_path):
    """Get unique contributors for a specific file."""
    result = subprocess.run(
        ["git", "blame", "--line-porcelain", file_path],
        stdout=subprocess.PIPE,
        text=True
    )
    authors = set()
    for line in result.stdout.splitlines():
        if line.startswith("author "):
            handle = line.split(" ", 1)[1]
            full_name = GITLAB_USERNAMES.get(handle, handle)  # Replace handle with full name if found
            authors.add(full_name)
    return authors

def get_git_dates(file_path):
    """Get the creation and last modified dates from git."""
    # Get the last modified date (most recent commit affecting the file)
    last_modified = subprocess.run(
        ["git", "log", "-1", "--format=%as", "--", file_path],
        stdout=subprocess.PIPE,
        text=True
    ).stdout.strip()

    # Get the creation date (first commit that added the file)
    created = subprocess.run(
        ["git", "log", "--reverse", "--format=%as", "--", file_path],
        stdout=subprocess.PIPE,
        text=True
    ).stdout.strip().splitlines()[0]

    return created, last_modified

def add_header_to_file(file_path, contributors):
    """Add a detailed header with contributors and other information."""
    created, last_modified = get_git_dates(file_path)
    header = (
        '"""\n'
        f"File: {os.path.basename(file_path)}\n"
        "Description: N/A\n\n"
        "Contributors:\n"
        + "\n".join(contributors) +
        f"\n\nCreated: {created}\n"
        f"Last Modified: {last_modified}\n\n"
        "Project: A Sign From Above\n"
        "URL: https://git.chalmers.se/courses/dit826/2024/group4\n\n"
        "License: MIT License (see LICENSE file for details)\n"
        '"""\n\n'
    )
    with open(file_path, "r+") as file:
        content = file.read()
        file.seek(0, 0)
        file.write(header + content)

def process_files(start_directory, extensions):
    """Iterate through all files and add headers."""
    for root, _, files in os.walk(start_directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    contributors = get_contributors(file_path)
                    if contributors:  # Only add a header if contributors exist
                        add_header_to_file(file_path, contributors)
                        print(f"Header added to {file_path}")
                except Exception as e:
                    print(f"Skipping {file_path} due to error: {e}")

def main():
    start_directory = os.getcwd()  # Use the current directory
    extensions = input("Enter file extensions to process (comma-separated, e.g., .py,.js): ").split(",")
    try:
        process_files(start_directory, extensions)
        print("Headers added to all applicable files successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
