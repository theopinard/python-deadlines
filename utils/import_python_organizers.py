from datetime import datetime
import pandas as pd
import urllib
import yaml
import sys
from pathlib import Path

sys.path.append(".")
from interactive_merge import fuzzy_match, interactive_merge
from utils import ordered_dump, get_schema


def load_remote(year):
    template = "https://raw.githubusercontent.com/python-organizers/conferences/main/{year}.csv"
    url = template.format(year=year)

    # Read data and rename columns
    df = pd.read_csv(url)
    df = map_columns(df)

    # Only return valid cfps
    # return df.dropna(subset=['cfp'])
    return df


def load_yml():
    schema = get_schema()

    # Load the YAML file
    with open("_data/conferences.yml", "r") as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    with open("_data/archive.yml", "r") as file:
        archive = yaml.load(file, Loader=yaml.FullLoader)

    # Convert the YAML data to a Pandas DataFrame
    return pd.concat(
        [schema, pd.DataFrame.from_dict(data), pd.DataFrame.from_dict(archive)],
        ignore_index=True,
    ).set_index("conference", drop=False)


def map_columns(df, reverse=False):
    cols = {
        "Subject": "conference",
        "Start Date": "start",
        "End Date": "end",
        "Tutorial Deadline": "tutorial_deadline",
        "Talk Deadline": "cfp",
        "Website URL": "link",
        "Proposal URL": "cfp_link",
        "Sponsorship URL": "sponsor",
    }

    df["place"] = df["Location"]

    if reverse:
        cols = {v: k for k, v in cols.items()}

    return df.rename(columns=cols)


def fill_missing_required(df):
    required = [
        "conference",
        "year",
        "link",
        "cfp",
        "timezone",
        "place",
        "start",
        "end",
        "sub",
    ]

    for i, row in df.copy().iterrows():
        for keyword in required:
            if pd.isna(row[keyword]):
                user_input = input(
                    f"What's the value of '{keyword}' for conference '{row['conference']}' check {row['link']} ?: "
                )
                if user_input != "":
                    df.loc[i, keyword] = user_input
    return df


def write_yaml(df, out_url):
    try:
        df = df.drop(["Country", "Venue"], axis=1)
    except KeyError:
        pass
    df["end"] = pd.to_datetime(df["end"]).dt.date
    df["start"] = pd.to_datetime(df["start"]).dt.date
    df["year"] = df["year"].astype(int)
    df["cfp"] = df["cfp"].astype(str)
    with open(out_url, "w") as outfile:
        for line in ordered_dump(
            [{k: v for k, v in record.items() if pd.notnull(v)} for record in df.to_dict(orient="records")],
            Dumper=yaml.SafeDumper,
            default_flow_style=False,
            explicit_start=True,
        ).splitlines():
            outfile.write(line.replace("- conference:", "\n- conference:"))
            outfile.write("\n")


def write_csv(df, year, csv_location):
    df["cfp"] = df["cfp"].str.slice(stop=10).str.replace("TBA", "")
    df["tutorial_deadline"] = df["tutorial_deadline"].str.slice(stop=10).str.replace("TBA", "")
    df = map_columns(df, reverse=True)
    for y in range(year, datetime.now().year + 10):
        if y in df["year"].unique():
            df.loc[
                df["year"] == y,
                [
                    "Subject",
                    "Start Date",
                    "End Date",
                    "Location",
                    "Country",
                    "Venue",
                    "Tutorial Deadline",
                    "Talk Deadline",
                    "Website URL",
                    "Proposal URL",
                    "Sponsorship URL",
                ],
            ].fillna("").astype(str).sort_values(by="Start Date").to_csv(Path(csv_location, f"{y}.csv"), index=False)


def main(year=None, base=""):
    target_file = Path(base, "_data", "conferences.yml")
    csv_location = Path(base, "utils", "conferences")

    if year is None:
        year = datetime.now().year

    df_yml = load_yml()
    df_new = pd.DataFrame(columns=df_yml.columns)
    df_csv = pd.DataFrame(columns=df_yml.columns)

    for y in range(year, datetime.now().year + 10):
        try:
            df = load_remote(year=y)
        except urllib.error.HTTPError:
            break

        if df_yml[df_yml["year"] == y].empty:
            df_csv = pd.concat([df_new, df], ignore_index=True)
        else:
            df_merged, df_remote = fuzzy_match(df_yml[df_yml["year"] == y], df)
            df_merged["year"] = y
            df_merged = df_merged.drop(["conference"], axis=1)
            df_merged = interactive_merge(df_merged, df_remote)

            df_new = pd.concat([df_new, df_merged], ignore_index=True)

            merged, _ = fuzzy_match(df, df_yml[df_yml["year"] == y])
            df_csv = pd.concat([df_csv, merged], ignore_index=True)

    df_new = fill_missing_required(df_new)
    write_yaml(df_new, target_file)

    df_csv.loc[:, "Location"] = df_csv.place
    write_csv(df_csv, year, csv_location)


if __name__ == "__main__":
    # Make argparse to get year and base

    import argparse

    parser = argparse.ArgumentParser(description="Import Python Organizers")
    parser.add_argument("--year", type=int, help="Year to import")

    main(year=parser.parse_args().year)
