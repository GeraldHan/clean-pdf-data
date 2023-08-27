import glob
import os
import shutil

def find_and_save_files(source_dir, dest_dir, type):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(type):
                file_path = os.path.join(root, file)
                save_path = os.path.join(dest_dir, file)
                shutil.copyfile(file_path, save_path)
                # os.remove(file_path)
                print(f"File {file_path} saved to {save_path}")

# Set the source directory and destination directory paths
source_dir = 'test_pdf'  # Replace with your source directory path
dest_dir = 'test_txt'  # Replace with your destination directory path
type = '.txt'

# Call the function to find and save ".txt" files
find_and_save_files(source_dir, dest_dir, type)