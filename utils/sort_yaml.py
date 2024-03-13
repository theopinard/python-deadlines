#!/usr/bin/env python3
# coding: utf-8

# Sort and Clean conference data.
# It writes to `"prefix"data.yml`, copy those to the conference.yml after screening.

import datetime
import pdb
import sys
import time
import urllib
from builtins import input
from pathlib import Path
from shutil import copyfile


import pytz
import requests
import yaml
from tqdm import tqdm

sys.path.append(".")
import link_check
from utils import pretty_print, ordered_dump, Loader, get_schema
from date_magic import clean_dates, create_nice_date

dateformat = "%Y-%m-%d %H:%M:%S"
tba_words = ["tba", "tbd", "cancelled"]


def sort_by_cfp(data):
    if "cfp" not in data:
        return "TBA"
    if data["cfp"] in ["TBA", "Cancelled"]:
        return data["cfp"]
    if not " " in data["cfp"]:
        data["cfp"] += " 23:59:00"
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


def sort_by_date(data):
    if "start" not in data:
        return "TBA"
    return str(data["start"])


def sort_by_date_passed(data):
    right_now = datetime.datetime.utcnow().replace(microsecond=0).strftime(dateformat)
    return sort_by_cfp(data) < right_now


def sort_by_year(data):
    return sort_by_cfp(data) < right_now


def order_keywords(data):
    schema = get_schema().columns.tolist()
    new_dict = {}
    for key in schema:
        if key in data:
            new_dict[key] = data[key]
    return new_dict


def merge_duplicates(data):
    filtered = []
    filtered_reduced = []
    for q in tqdm(data):
        q_reduced = f'{q["conference"]} {q["year"]}'
        if q_reduced not in filtered_reduced:
            filtered.append(q)
            filtered_reduced.append(q_reduced)
        else:
            index = filtered_reduced.index(q_reduced)
            for key, value in q.items():
                if value and key not in filtered[index]:
                    filtered[index][key] = value
                else:
                    if len(str(value)) > len(str(filtered[index][key])):
                        filtered[index][key] = value
    return filtered


def split_data(data):
    conf, tba, expired = [], [], []
    for q in tqdm(data):
        if q.get("end", datetime.datetime.utcnow().replace(microsecond=0).date()) < datetime.datetime.utcnow().replace(
            microsecond=0
        ).date() - datetime.timedelta(days=37):
            expired.append(q)
            continue

        q = clean_dates(q)
        q = create_nice_date(q)

        try:
            if q["cfp"].lower() in tba_words:
                tba.append(q)
            else:
                if " " not in q["cfp"]:
                    q["cfp"] += " 23:59:00"
                conf.append(q)
        except:
            print(data["cfp"].lower(), tba_words)
    return conf, tba, expired


def add_latlon(data):
    cache = {}

    data_copy = []

    # Build Cache
    for i, q in tqdm(enumerate(data), total=len(data)):
        if ("place" not in q) or ("online" in q["place"].lower()):
            continue
        elif "location" in q:
            cache[q["place"]] = q["location"]
            continue
        else:
            data_copy.append((i, q))

    for i, q in tqdm(data_copy):
        try:
            q["place"] = q["place"].split(",")[0].strip() + ", " + q["place"].split(",")[-1].strip()
        except IndexError:
            print(f"IndexError: {q['place']}")

        if q["place"] in cache and cache[q["place"]] is not None:
            data[i]["location"] = {
                "latitude": cache[q["place"]]["latitude"],
                "longitude": cache[q["place"]]["longitude"],
            }

        else:
            url = (
                "https://nominatim.openstreetmap.org/search"
                + "?format=json&q="
                + urllib.parse.quote(q["place"])
            )
            response = requests.get(url)

            if response:
                try:
                    response = response.json()
                    data[i]["location"] = {
                        "latitude": float(response[0]["lat"]),
                        "longitude": float(response[0]["lon"]),
                    }
                    cache[q["place"]] = data[i]["location"]
                except IndexError:
                    cache[q["place"]] = None
                    print(f"No response from Openstreetmaps for {q['place']}")
                time.sleep(2)
            else:
                cache[q["place"]] = None
                print(f"No response from Openstreetmaps for {q['place']}")
    return data


def check_links(data):
    cache = {}
    for q in tqdm(data):
        if "link" in q:
            if q["link"] in cache:
                q["link"] = cache[q["link"]]
            else:
                new_link = link_check.check_link_availability(q["link"], q["start"])
                cache[q["link"]] = q["link"]
                cache[new_link] = new_link
                q["link"] = new_link
            time.sleep(0.5)
    return data


# Sort:
def sort_data(base="", prefix=""):
    url = Path(base, "_data", "conferences.yml")
    out_url = Path(base, "_data", f"{prefix}conferences.yml")
    archive = Path(base, "_data", "archive.yml")
    out_archive = Path(base, "_data", f"{prefix}archive.yml")

    with open(url, "r") as stream:
        try:
            data = yaml.load(stream, Loader=Loader)

            print("Initial Sorting:")
            for i, q in enumerate(data.copy()):
                print(q["cfp"], " - ", q["conference"])
                data[i] = order_keywords(q)

            print("\n\n")

            # Geocode Data
            print("Adding Lat Lon from Place")
            data = add_latlon(data)

            # Merge duplicates
            print("Merging duplicates")
            data = merge_duplicates(data)

            # Check Links
            # print("Checking Links")
            # data = check_links(data)

            # Split data by cfp
            print("Splitting conferences, tba, and archive")
            conf, tba, expired = split_data(data)

            # just sort:
            conf.sort(key=sort_by_cfp, reverse=True)
            pretty_print("Date Sorting:", conf, tba, expired)
            conf.sort(key=sort_by_date_passed)
            pretty_print("Date and Passed Deadline Sorting with tba:", conf, tba, expired)

            with open(out_url, "w") as outfile:
                for line in ordered_dump(
                    conf + tba,
                    Dumper=yaml.SafeDumper,
                    default_flow_style=False,
                    explicit_start=True,
                ).splitlines():
                    outfile.write(line.replace("- conference:", "\n- conference:"))
                    outfile.write("\n")
        except yaml.YAMLError as exc:
            print(exc)

    with open(archive, "r") as stream:
        try:
            data = yaml.load(stream, Loader=Loader)

            for old in expired:
                if old not in data:
                    data.append(old)

            for i, q in enumerate(data.copy()):
                data[i] = order_keywords(q)

            # Merge duplicates
            data = merge_duplicates(data)

            # Check Links
            # data = check_links(data)

            # Geocode Data
            data = add_latlon(data)

            data.sort(key=sort_by_date, reverse=True)
            data.sort(key=sort_by_cfp, reverse=True)

            pretty_print("New archive:", data)
            with open(out_archive, "w") as outfile:
                for line in ordered_dump(
                    data,
                    Dumper=yaml.SafeDumper,
                    default_flow_style=False,
                    explicit_start=True,
                ).splitlines():
                    outfile.write(line.replace("- conference:", "\n- conference:"))
                    outfile.write("\n")
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == "__main__":
    sort_data()
