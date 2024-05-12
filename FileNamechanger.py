import os
import re
import sys

# Get the folder path where this script (or the compiled EXE) is located
folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))

# Get the name of the script or the compiled EXE
script_or_exe_name = os.path.basename(sys.argv[0])

print(f"Ali's Filename Changer\n\n")
print(f"This will rename every file in the same folder as the executable.\nIt will find any filename that matches the search pattern you provide and replace the match with the replacement string.\nWorks with RegEx patterns and capture groups. \\1 to refer to the first capture group.\nWARNING: You won't be able to Ctrl-Z this action!\n")
# Ask the user for the regex pattern and replacement string
pattern_to_search = input("Enter the regex pattern to search for: ")
replacement_string = input("Enter the replacement string: ")

input_check = input("Are you sure? y/n")

if input_check == "y":
    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        # Check if the file is the script or the EXE itself, if so, skip it
        if filename == script_or_exe_name:
            continue

        # Check if the current file name matches the search pattern
        if re.search(pattern_to_search, filename):
            # Create the new name by replacing the found pattern
            new_name = re.sub(pattern_to_search, replacement_string, filename)
            # Generate full file paths
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_name)
            # Rename the file
            os.rename(old_file_path, new_file_path)
            print(f"Renamed '{filename}' to '{new_name}'")

input("Press Enter to exit...")