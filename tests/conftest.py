import sys
import os

# Get the path of the parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(parent_dir)

# Modify the path for importing the module
sys.path.insert(0, parent_dir)
