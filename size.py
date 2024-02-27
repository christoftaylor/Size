#!python3
#
# A script that lists the files and directories, sorted by size
# Sizes for directories are the sum total of all objects recursively within them
# This could have been `du --max-depth=1 -h | sort -h`, but sort on my NAS doesn't do -h
#

import argparse
import os
import sys
import pwd
import grp
import stat
import datetime
import humanize


# Recurse through a path adding the size of each file to the total size for the directory
#
def get_total_size(path):
    total_size = 0
    try:
        if os.path.isfile(path):
            total_size += os.path.getsize(path)
        elif os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path, onerror=lambda e: print(f"Error accessing {e.filename}: {e}")):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (PermissionError, IsADirectoryError, FileNotFoundError) as e:
                        if isinstance(e, PermissionError):
                            print(f"PermissionError accessing {filepath}: {e} (skipped)")
                    except Exception as e:
                        print(f"Error accessing {filepath}: {e}")
        else:
            print(f"Unknown item type: {path}")
    except (PermissionError, IsADirectoryError, FileNotFoundError) as e:
        if isinstance(e, PermissionError):
            print(f"PermissionError accessing {path}: {e} (skipped)")
        elif isinstance(e, IsADirectoryError):
            print(f"IsADirectoryError accessing {path}: {e} (skipped)")
        else:
            print(f"Error accessing {path}: {e}")

    return total_size


# List the items in directory, sorted by size, printed into pretty columns
#
def list_files_and_directories_by_size(directory, verbose, reverse):
    items = []
    max_lengths = {'Owner': 0, 'Group': 0, 'Name': 0}

    # step through each item in directory, saving key stats on each
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        mode = stat.filemode(os.lstat(path).st_mode)
        mtime = datetime.datetime.fromtimestamp(os.lstat(path).st_mtime)
        owner = pwd.getpwuid(os.lstat(path).st_uid).pw_name
        group = grp.getgrgid(os.lstat(path).st_gid).gr_name

        # if the item is a symlink, include target in name
        if os.path.islink(path):
            name = name + " -> " + os.readlink(path)

        # update the max lengths keys for each string column in output
        for key, value in {'Owner': owner, 'Group': group, 'Name': name}.items():
            max_lengths[key] = max(max_lengths[key], len(str(value)))

        # add all that data into array
        items.append((get_total_size(path), mode, owner, group, mtime, name, path))

    # sort the array based on the first column, which happens to be the size
    if reverse:
        items.sort(key=lambda x: x[0], reverse=True)
    else:
        items.sort(key=lambda x: x[0])

    # set the print formats
    if verbose:
        row_format = "{:>12}  {:<10}  {:>{width[Owner]}}:{:<{width[Group]}}  {:<16}  {:<{width[Name]}}"
    else:
        row_format = "{:>12}  {:<{width[Name]}}"

    # print the header
    if verbose:
        print(row_format.format("Size", "Mode", "Owner", "Group", "Last Modified", "Name", width=max_lengths))
        print("-" * (47 + sum(max_lengths.values())))
    else:
        print(row_format.format("Size", "Name", width=max_lengths))
        print("-" * (14 + max_lengths['Name']))

    # print the stuff
    for size, mode, owner, group, mtime, name, path in items:
        if verbose:
            print(row_format.format(humanize.naturalsize(size, True, True), mode, owner, group, mtime.strftime('%Y-%m-%d %H:%M'), name, width=max_lengths))
        else:
            print(row_format.format(humanize.naturalsize(size, True, True), name, width=max_lengths))


# Do the main thing
#
if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Prints out directory listing sorted by total recursive size for directories.')
    parser.add_argument('-v', '--verbose', required=False,
                        dest='verbose', default=False, action='store_true',
                        help='Include more columns in output.')
    parser.add_argument('-r', '--reverse', required=False,
                        dest='reverse', default=False, action='store_true',
                        help='Reverse the sort order to put big stuff at the top.')
    parser.add_argument('path', 
                        nargs='?', default=os.getcwd(),
                        help='Optional. The starting path. Current directory if not specified.')
    args = parser.parse_args()
    verbose = args.verbose
    if verbose: print('Verbose output is on')
  
    if os.path.exists(args.path):
        if verbose: print('Path = {}'.format(os.path.abspath(args.path)))
        list_files_and_directories_by_size(args.path, args.verbose, args.reverse)
    else:
        print("Invalid directory path.")

