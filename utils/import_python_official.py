import pandas as pd
from icalendar import Calendar
from urllib import request
import re
import yaml


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
            end = component.get("dtend").dt
            # If the event is all day, the date might be of type 'date' (instead of 'datetime')
            # Adjust format accordingly
            start = start.strftime("%Y-%m-%d")
            end = end.strftime("%Y-%m-%d")
            year = start[:4]

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


# Use the function to parse your .ics file
df = ics_to_dataframe()

with open("df.yml", "w") as file:
    yaml.dump({"result": df.to_dict(orient="records")}, file, default_flow_style=False)

# Display the DataFrame
print(df)
