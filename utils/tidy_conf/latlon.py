import requests
from tqdm import tqdm


import time
import urllib


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
                    print(f"No response from Openstreetmaps for {q['place']}")
                time.sleep(2)
            else:
                cache[q["place"]] = None
                print(f"No response from Openstreetmaps for {q['place']}")
    return data
