import requests
from tqdm import tqdm


import time
import urllib


def add_latlon(data):
    """Add latitude and longitude to the data."""

    # Cache for locations
    cache = {}
    # Copy of data for unlocated conferences
    data_copy = []

    # Go through the data and check if the location is already in the cache
    for i, q in tqdm(enumerate(data), total=len(data)):
        if ("place" not in q) or ("online" in q["place"].lower()):
            # Ignore online conferences
            continue
        elif "location" in q:
            # If location is already present, add it to the cache
            cache[q["place"]] = q["location"]
            continue
        else:
            # Add to the copy if location is not present for speed
            data_copy.append((i, q))

    # Go through the copy and get the latitude and longitude
    for i, q in tqdm(data_copy):
        # Get a shorter location
        try:
            q["place"] = q["place"].split(",")[0].strip() + ", " + q["place"].split(",")[-1].strip()
        except IndexError:
            tqdm.write(f"IndexError: {q['place']}")

        # Check if the location is already in the cache
        if q["place"] in cache and cache[q["place"]] is not None:
            data[i]["location"] = {
                "latitude": cache[q["place"]]["latitude"],
                "longitude": cache[q["place"]]["longitude"],
            }

        else:
            # Get the location from Openstreetmaps
            url = "https://nominatim.openstreetmap.org/search" + "?format=json&q=" + urllib.parse.quote(q["place"])
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
                    tqdm.write(f"No response from Openstreetmaps for {q['place']}")
                time.sleep(2)
            else:
                cache[q["place"]] = None
                tqdm.write(f"No response from Openstreetmaps for {q['place']}")
    return data
