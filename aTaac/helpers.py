import os
import csv
from dotenv import load_dotenv

# ## write_file
#
# Writes a file to the `io` directory.
#
# * **fname**: The file name as string.
# * **command**: The type of command issued as a string.
#
# **returns**: None.

# In[2]:
load_dotenv()
root_path = os.getenv("ROOT_PATH")


def write_file(fname: str, command: str) -> None:
    with open(f"{root_path}/{fname}", "w") as f:  # not appending on purpose
        f.write(command)


# ## read_file
#
# Read a file from the `io` directory and return the file contents.
#
# * **fname**: The file name as string.
#
# **returns**: Contents of the file.

def read_file(fname: str) -> str:
    with open(f"{root_path}/{fname}") as f:
        return f.read()


# ## write_logging_files
#
# Takes in file names and checks if the files exist in the `io` directory. If files don't exist, files are created.
#
# * **exploit_file_3x3**: String representing a filename.
# * **exploit_file_3x3**: String representing a filename.
# * **set_file_5x5**: String representing a filename.
#
# **returns**: None

def write_logging_files(exploit_file_3x3: str, exploit_file_5x5: str, set_file_5x5: str) -> None:
    files = [exploit_file_3x3, exploit_file_5x5, set_file_5x5]
    for f in files:
        if not os.path.isfile(f"{root_path}/{f}"):
            write_file(f, "")


def write_csv(filename, row):
    # writing to csv file
    with open(f"{root_path}/{filename}", 'a') as csvfile:
        csv.writer(csvfile).writerow(row)
