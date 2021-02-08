import os
import sys

# we do this to import like from root files
file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(file_dir)
sys.path.append(parent_dir)


def file_delete(file_name):
    if os.path.exists(file_name):
        print('remove ' + file_name)
        os.remove(file_name)