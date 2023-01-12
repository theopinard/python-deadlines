#!/usr/bin/env python3
# coding: utf-8

# Sort and Clean conference data.
# It writes to `sorted_data.yml` and `cleaned_data.yml`, copy those to the conference.yml after screening.

import datetime
import pdb
import sys
from builtins import input
from pathlib import Path
from shutil import copyfile

import pytz
import yaml

try:
    # for python newer than 2.7
    from collections import OrderedDict
except ImportError:
    # use backport from pypi
    from ordereddict import OrderedDict

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

from yaml.representer import SafeRepresenter

_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())


def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))


Dumper.add_representer(OrderedDict, dict_representer)
Loader.add_constructor(_mapping_tag, dict_constructor)

Dumper.add_representer(str, SafeRepresenter.represent_str)


def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


dateformat = "%Y-%m-%d %H:%M:%S"
tba_words = ["tba", "tbd"]

# Helper function for yes no questions
def query_yes_no(question, default="no"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def sort_by_cfp(data):
    return pytz.utc.normalize(
        datetime.datetime.strptime(data["cfp"], dateformat).replace(
            tzinfo=pytz.timezone(
                data.get("timezone", "AoE")
                .replace("AoE", "Etc/GMT+12")
                .replace("UTC+", "Etc/GMT-")
                .replace("UTC-", "Etc/GMT+")
            )
        )
    ).strftime(dateformat)


def sort_by_date_passed(data):
    right_now = datetime.datetime.utcnow().replace(microsecond=0).strftime(dateformat)
    return sort_by_cfp(data) < right_now


def split_data(data):
    conf, tba, expired = [], [], []
    for q in data:
        if q.get("end", datetime.datetime.utcnow().replace(microsecond=0).date()) < datetime.datetime.utcnow().replace(
            microsecond=0
        ).date() - datetime.timedelta(days=66):
            expired.append(q)
            continue

        try:
            if q["cfp"].lower() in tba_words:
                tba.append(q)
            else:
                conf.append(q)
        except:
            print(data["cfp"].lower(), tba_words)
    return conf, tba, expired


def pretty_print(header, conf, tba=None, expired=None):
    print(header)
    for data in [conf, tba, expired]:
        if data is not None:
            for q in data:
                print(q["cfp"], " - ", q["title"])
            print("\n")


# Sort:
def sort_data(base=""):
    url = Path(base, "_data", "conferences.yml")
    out_url = Path(base, "utils", "sorted_data.yml")
    archive = Path(base, "_data", "archive.yml")
    out_archive = Path(base, "utils", "sorted_archive.yml")

    with open(url, "r") as stream:
        try:
            data = yaml.load(stream, Loader=Loader)
            print("Initial Sorting:")
            for q in data:
                print(q["cfp"], " - ", q["title"])
            print("\n\n")

            conf, tba, expired = split_data(data)

            # just sort:
            conf.sort(key=sort_by_cfp, reverse=True)
            pretty_print("Date Sorting:", conf, tba, expired)
            conf.sort(key=sort_by_date_passed)
            pretty_print("Date and Passed Deadline Sorting with tba:", conf, tba, expired)

            with open(out_url, "w") as outfile:
                for line in ordered_dump(
                    conf + tba, Dumper=yaml.SafeDumper, default_flow_style=False, explicit_start=True
                ).splitlines():
                    outfile.write(line.replace("- title:", "\n- title:"))
                    outfile.write("\n")
        except yaml.YAMLError as exc:
            print(exc)

    with open(archive, "r") as stream:
        try:
            data = yaml.load(stream, Loader=Loader)

            pretty_print("Old archive:", data)

            data += expired

            data.sort(key=sort_by_cfp, reverse=True)

            pretty_print("New archive:", data)

            with open(out_archive, "w") as outfile:
                for line in ordered_dump(
                    data, Dumper=yaml.SafeDumper, default_flow_style=False, explicit_start=True
                ).splitlines():
                    outfile.write(line.replace("- title:", "\n- title:"))
                    outfile.write("\n")
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == "__main__":
    sort_data()
