import sys

sys.path.append(".")
from sort_yaml import sort_data
from import_python_organizers import main as organizer_updater
from import_python_official import main as official_updater

if __name__ == "__main__":
    official_updater()
    sort_data()
    organizer_updater()
    sort_data()
