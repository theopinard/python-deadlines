from pathlib import Path
import pandas as pd
from icalendar import Calendar
from urllib import request
import re

from datetime import datetime, timedelta
import sys

sys.path.append(".")
from tidy_conf.utils import fill_missing_required
from tidy_conf.yaml import write_df_yaml
from tidy_conf import load_conferences, fuzzy_match, merge_conferences


def ics_to_dataframe():
    # Open the .ics file and parse it into a Calendar object
    with request.urlopen(
        "https://www.google.com/calendar/ical/j7gov1cmnqr9tvg14k621j7t5c@group.calendar.google.com/public/basic.ics"
    ) as file:
        calendar = Calendar.from_ical(file.read())

    link_desc = re.compile(r".*<a .*?href=\"? ?((?:https|http):\/\/[\w0-9\.\/\-\?= ]+)\"?.*?>(.*?)[#0-9 ]*<\/?a>.*")

    # Initialize a list to hold event data
    event_data = []

    # Iterate over each event in the Calendar
    for component in calendar.walk():
        if component.name == "VEVENT":
            # Extract event details
            conference = str(component.get("summary"))
            start = component.get("dtstart").dt
            end = component.get("dtend").dt - timedelta(days=1)
            # If the event is all day, the date might be of type 'date' (instead of 'datetime')
            # Adjust format accordingly
            start = start.strftime("%Y-%m-%d")
            end = end.strftime("%Y-%m-%d")
            year = int(start[:4])

            description = re.sub(
                r"(?:\\s|&nbsp;|\\|\'|<br />|<br>|</[^a][^>]*>|<[^a/][^>]*>)+",
                " ",
                "<a "
                + "<a ".join(
                    str(component.get("description"))
                    .replace("\n", "")
                    .replace("”", '"')
                    .replace("“", '"')
                    .replace("&amp;", "&")
                    .replace("&quot;", '"')
                    .replace("&apos;", "'")
                    .replace("&lt;", "<")
                    .replace("&gt;", ">")
                    .split("<a ")[1:]
                ),
            )

            try:
                m = re.match(link_desc, description)
                link = m.group(1).strip()
                conference2 = m.group(2).strip()
            except AttributeError:
                print(m)
                print("." + description + " | " + re.escape(str(component.get("description"))) + ".")
                continue

            if conference2 != "":
                conference = conference2
            location = str(component.get("location"))

            # Append this event's details to the list
            event_data.append([conference, year, "TBA", start, end, link, location])

    # Convert the list into a pandas DataFrame
    df = pd.DataFrame(event_data, columns=["conference", "year", "cfp", "start", "end", "link", "place"])

    return df


def main(year=None, base=""):
    if year is None:
        year = datetime.now().year

    target_file = Path(base, "_data", "conferences.yml")

    df_yml = load_conferences()
    df_new = pd.DataFrame(columns=df_yml.columns)

    # Use the function to parse your .ics file
    df = ics_to_dataframe()
    df = df.loc[pd.to_datetime(df["start"]) > pd.Timestamp(datetime.now())]
    df = df.loc[df["year"] == year]

    print(df)

    df_merged, df_remote = fuzzy_match(df_yml[df_yml["year"] == year], df)
    df_merged["year"] = year
    df_merged = df_merged.drop(["conference"], axis=1)
    df_merged = merge_conferences(df_merged, df_remote)

    df_new = pd.concat([df_new, df_merged], ignore_index=True)

    df_new = fill_missing_required(df_new)

    write_df_yaml(df_new, target_file)


if __name__ == "__main__":
    # Make argparse to get year and base

    import argparse

    parser = argparse.ArgumentParser(description="Import Python Organizers")
    parser.add_argument("--year", type=int, help="Year to import")

    main(year=parser.parse_args().year)
